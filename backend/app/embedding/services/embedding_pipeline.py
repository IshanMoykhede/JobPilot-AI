import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.embedding.core import embedding_config
from app.embedding.services.candidate_document_builder import CandidateDocumentBuilder
# from app.embedding.services.job_document_builder import JobDocumentBuilder
from app.embedding.services.embedding_provider import FastEmbedEmbeddingProvider, MockEmbeddingProvider
from app.vector_store.services.vector_store_service import VectorStoreService
from app.vector_store.core import vector_store_config

# Import PostgreSQL models to retrieve knowledge structures
from app.models.candidate_insights import CandidateInsights
# from app.job_search.models.job_knowledge import JobKnowledge
# from app.job_search.models.job_search_result import JobSearchResult
# from app.job_search.core.job_enums import JobProcessingStatus

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
                logger.error(f"[EmbeddingPipeline] Failed to load FastEmbed provider: {e}.")
                raise RuntimeError(f"Embedding Provider Initialization Failed: {e}")
        
        raise RuntimeError("Embedding provider could not be initialized. Provider not recognized or fastembed failed.")

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

    # @staticmethod
    # async def generate_job_embeddings_for_workspace(db: Session, workspace_id: uuid.UUID) -> None:
    #     pass
