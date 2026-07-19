import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.embedding.core import embedding_config
from app.embedding.services.candidate_document_builder import CandidateDocumentBuilder
from app.embedding.services.job_document_builder import JobDocumentBuilder
from app.embedding.services.embedding_provider import FastEmbedEmbeddingProvider, MockEmbeddingProvider
from app.vector_store.services.vector_store_service import VectorStoreService
from app.vector_store.core import vector_store_config

# Import PostgreSQL models to retrieve knowledge structures
from app.models.candidate_insights import CandidateInsights
from app.job_search.models.job_knowledge import JobKnowledge
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.core.job_enums import JobProcessingStatus

logger = logging.getLogger(__name__)

class EmbeddingGenerationPipeline:
    @staticmethod
    def _get_provider():
        """
        Dynamically instantiates the configured embedding provider.
        """
        provider_name = embedding_config.EMBEDDING_PROVIDER.lower()
        if provider_name == "fastembed":
            try:
                return FastEmbedEmbeddingProvider(model_name=embedding_config.EMBEDDING_MODEL)
            except Exception as e:
                if settings.ENABLE_EMBEDDINGS:
                    logger.error(f"[EmbeddingPipeline] Failed to load FastEmbed provider: {e}.")
                    raise RuntimeError(f"Embedding Provider Initialization Failed: {e}")
        
        raise RuntimeError("Embedding provider could not be initialized. ENABLE_EMBEDDINGS is false or fastembed failed.")

    @staticmethod
    async def generate_candidate_embedding(db: Session, candidate_knowledge_id: uuid.UUID) -> bool:
        """
        Builds, generates embedding, and persists Candidate Knowledge vector.
        """
        logger.info(f"[EmbeddingPipeline] Starting candidate embedding generation for ID {candidate_knowledge_id}")
        
        print(f"\n[{'='*50}]")
        print("--> ENTERING STAGE: CANDIDATE EMBEDDING GENERATION")
        print(f"--> Input Candidate Knowledge ID: {candidate_knowledge_id}")

        # Load Candidate Insights record (which holds the CandidateKnowledge JSON)
        insight = db.query(CandidateInsights).filter(CandidateInsights.id == candidate_knowledge_id).first()
        if not insight or not insight.artifact_json:
            logger.error(f"[EmbeddingPipeline] Candidate insights record {candidate_knowledge_id} or its JSON payload not found.")
            print(f"--> Output Candidate Embedding Status: Failed (Insight record or payload missing)")
            print(f"[{'='*50}]\n")
            return False

        # 1. Build Semantic Document
        doc = CandidateDocumentBuilder.build_document(insight.artifact_json)
        logger.info("[EmbeddingPipeline] Semantic document built.")
        print("--> Built Semantic Document for Vector Store:")
        print(doc)

        model_name = embedding_config.EMBEDDING_MODEL
        schema_version = embedding_config.EMBEDDING_SCHEMA_VERSION
        collection = vector_store_config.CANDIDATE_COLLECTION

        # 2. Generate Embedding Vector
        logger.info("[EmbeddingPipeline] Generating candidate embedding.")
        provider = EmbeddingGenerationPipeline._get_provider()
        try:
            vector = provider.generate_embedding(doc)
        except Exception as e:
            logger.error(f"[EmbeddingPipeline] Critical Embedding Provider failure: {e}.")
            print(f"--> Output Candidate Embedding Status: Failed (Provider error: {e})")
            print(f"[{'='*50}]\n")
            return False

        # 3. Persist to Vector Store
        candidate_identity = insight.artifact_json.get("candidate_identity", {})
        domains = candidate_identity.get("engineering_domains") or []
        primary_domain = domains[0] if domains else "Unknown"
        secondary_domains = domains[1:] if len(domains) > 1 else []
        
        payload = {
            "candidate_knowledge_id": str(candidate_knowledge_id),
            "candidate_profile_id": str(insight.candidate_profile_id),
            "embedding_model": model_name,
            "embedding_schema_version": schema_version,
            "primary_domain": primary_domain,
            "secondary_domains": secondary_domains,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        point_id = str(uuid.uuid4())
        try:
            VectorStoreService.upsert(collection, point_id, vector, payload)
            logger.info(f"[EmbeddingPipeline] Candidate embedding successfully stored in collection '{collection}'.")
            print("--> Output Candidate Embedding Status: Success")
            print(f"[{'='*50}]\n")
        except Exception as e:
            logger.error(f"[EmbeddingPipeline] Failed to upsert candidate embedding to Qdrant: {e}")
            print(f"--> Output Candidate Embedding Status: Failed (Qdrant error: {e})")
            print(f"[{'='*50}]\n")
            raise RuntimeError(f"Critical vector database failure: {e}")
            
        return True

    @staticmethod
    async def generate_job_embeddings_for_workspace(db: Session, workspace_id: uuid.UUID) -> None:
        """
        Builds, batches, and uploads Job Knowledge vectors for a workspace using strict pipeline rules.
        """
        import asyncio
        logger.info(f"[EmbeddingPipeline] Starting job embeddings generation for workspace {workspace_id}")
        
        # 1. Load KNOWLEDGE_GENERATED Jobs
        job_results = db.query(JobSearchResult).filter(
            JobSearchResult.workspace_id == workspace_id,
            JobSearchResult.processing_status == JobProcessingStatus.KNOWLEDGE_GENERATED
        ).all()

        if not job_results:
            logger.info("[EmbeddingPipeline] No job results require embedding in this workspace.")
            return

        logger.info(f"[EmbeddingPipeline] Found {len(job_results)} jobs.")

        collection = vector_store_config.JOB_COLLECTION
        provider = EmbeddingGenerationPipeline._get_provider()
        model_name = embedding_config.EMBEDDING_MODEL
        schema_version = "v2-structured"

        # 2. Serialize to Semantic Documents
        valid_jobs = []
        has_serialization_errors = False
        for job_res in job_results:
            jk = job_res.job_knowledge
            if not jk:
                logger.error(f"[EmbeddingPipeline] JobResult {job_res.id} missing JobKnowledge. Marking FAILED.")
                job_res.processing_status = JobProcessingStatus.FAILED
                has_serialization_errors = True
                continue
                
            try:
                doc = JobDocumentBuilder.build_document(jk)
                valid_jobs.append({
                    "job_res": job_res,
                    "job_knowledge": jk,
                    "semantic_document": doc
                })
            except Exception as e:
                logger.error(f"[EmbeddingPipeline] Failed to serialize JobKnowledge for {jk.id}: {e}")
                job_res.processing_status = JobProcessingStatus.FAILED
                has_serialization_errors = True

        if has_serialization_errors:
            db.commit()

        if not valid_jobs:
            return

        # 3. Batching
        batch_size = embedding_config.EMBEDDING_BATCH_SIZE
        semaphore = asyncio.Semaphore(5)

        async def _process_embedding_batch(batch: List[Dict[str, Any]]):
            async with semaphore:
                documents = [item["semantic_document"] for item in batch]
                
                # 4. Vectorization (No silent mock fallback in production)
                logger.info(f"[EmbeddingPipeline] Generating embeddings for batch of {len(batch)} jobs.")
                try:
                    vectors = provider.generate_embeddings_batch(documents)
                except Exception as batch_err:
                    logger.error(f"[EmbeddingPipeline] Critical Embedding Provider failure: {batch_err}")
                    # Mark all jobs in this batch as FAILED, preserving diagnostic info
                    for item in batch:
                        item["job_res"].processing_status = JobProcessingStatus.FAILED
                    db.commit()
                    return

                # 5. Prepare Qdrant Payload
                points = []
                for i, item in enumerate(batch):
                    job_res = item["job_res"]
                    jk = item["job_knowledge"]
                    
                    # Convert enums safely
                    primary_domain_val = str(jk.primary_domain.value if hasattr(jk.primary_domain, "value") else jk.primary_domain)
                    emp_level_val = str(jk.employment_level.value if hasattr(jk.employment_level, "value") else jk.employment_level) if jk.employment_level else None

                    payload = {
                        "job_hash": jk.job_hash,
                        "embedding_version": schema_version,
                        "embedding_model": model_name,
                        "job_search_result_id": str(job_res.id),
                        "job_knowledge_id": str(jk.id),
                        "workspace_id": str(workspace_id),
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Only add keys that contain truthy values (used for potential future filtering)
                    if jk.job_title: payload["job_title"] = jk.job_title
                    if jk.company_name: payload["company_name"] = jk.company_name
                    if jk.location: payload["location"] = jk.location
                    if jk.employment_type: payload["employment_type"] = jk.employment_type
                    if jk.work_mode: payload["work_mode"] = jk.work_mode
                    if jk.industry: payload["industry"] = jk.industry
                    if emp_level_val: payload["employment_level"] = emp_level_val
                    if primary_domain_val: payload["primary_domain"] = primary_domain_val
                    if jk.secondary_domains: payload["secondary_domains"] = jk.secondary_domains

                    points.append({
                        "id": str(job_res.id),
                        "vector": vectors[i],
                        "payload": payload
                    })

                # 6. Qdrant Upsert and State Sync
                try:
                    VectorStoreService.upsert_batch(collection, points)
                    for item in batch:
                        item["job_res"].processing_status = JobProcessingStatus.EMBEDDED
                        item["job_res"].embedding_generated_at = datetime.now(timezone.utc)
                    db.commit()
                    logger.info(f"[EmbeddingPipeline] Stored {len(points)} job vectors successfully.")
                except Exception as upsert_err:
                    db.rollback()
                    logger.error(f"[EmbeddingPipeline] Failed to store batch vectors to Qdrant: {upsert_err}")
                    for item in batch:
                        item["job_res"].processing_status = JobProcessingStatus.FAILED
                    db.commit()

        # Group into chunks
        tasks = []
        for index in range(0, len(valid_jobs), batch_size):
            batch = valid_jobs[index : index + batch_size]
            tasks.append(_process_embedding_batch(batch))
            
        await asyncio.gather(*tasks)
