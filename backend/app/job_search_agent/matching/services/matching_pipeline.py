import logging
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.candidate_insights import CandidateInsights, ArtifactType, InsightStatus
from app.job_search.models.job_knowledge import JobKnowledge
from app.job_search.models.job_search_result import JobSearchResult

from app.job_search_agent.matching.schemas.matching import MatchingContext
from app.job_search_agent.matching.schemas.matching_result import RankedJob
from app.job_search_agent.matching.services.semantic_matcher import SemanticMatcher
from app.job_search_agent.matching.services.hybrid_matcher import HybridMatcher
from app.job_search_agent.matching.services.ranking_service import RankingService

from app.vector_store.services.vector_store_service import VectorStoreService
from app.vector_store.core import vector_store_config

from app.job_search_agent.matching.services.llm_comparison_service import LLMComparisonService
from app.job_search_agent.matching.services.deterministic_matcher import DeterministicMatcher
from app.embedding.services.candidate_document_builder import CandidateDocumentBuilder
from app.job_search_agent.matching.schemas.comparison import MatchKnowledge, CandidateContext

logger = logging.getLogger(__name__)

class MatchingPipeline:
    @staticmethod
    async def run_matching_pipeline(
        db: Session,
        candidate_profile_id: uuid.UUID,
        workspace_id: uuid.UUID,
        conversation_id: Optional[uuid.UUID] = None
    ) -> List[RankedJob]:
        """
        Orchestrates the hybrid matching flow:
        1. Fetch Candidate Vector (Phase 1)
        2. Run Semantic similarity lookup (Phase 1)
        3. Run LLM Structured Comparison (Phase 2)
        4. Run Deterministic Scoring (Phase 3)
        5. Persist MatchKnowledge to Postgres
        """
        logger.info(f"[MatchingPipeline] Starting hybrid matching engine for candidate_profile={candidate_profile_id}, workspace={workspace_id}")

        # 1. Retrieve latest candidate knowledge insights
        insight = db.query(CandidateInsights).filter(
            CandidateInsights.candidate_profile_id == candidate_profile_id,
            CandidateInsights.artifact_type == ArtifactType.CANDIDATE_KNOWLEDGE,
            CandidateInsights.status == InsightStatus.COMPLETED
        ).order_by(CandidateInsights.created_at.desc()).first()

        if not insight or not insight.artifact_json:
            raise ValueError(f"No completed candidate knowledge artifact found for profile {candidate_profile_id}")

        # 2. Retrieve Candidate Vector from vector store
        res = VectorStoreService.get(
            collection_name=vector_store_config.CANDIDATE_COLLECTION,
            filter_field="candidate_knowledge_id",
            filter_value=str(insight.id)
        )
        if not res or not res.get("vector"):
            raise ValueError(f"Candidate embedding vector not found in index for knowledge ID {insight.id}")
            
        candidate_vector = res["vector"]

        # Phase 2 prep: Build the Candidate Semantic Profile exactly once
        candidate_semantic_doc = CandidateDocumentBuilder.build_document(insight.artifact_json)

        # 3. Retrieve raw job matches from Vector Store
        workspace_jobs = db.query(JobSearchResult).filter(JobSearchResult.workspace_id == workspace_id).all()
        
        if not workspace_jobs:
            logger.info(f"[MatchingPipeline] No job search results found for workspace {workspace_id}")
            return []

        job_search_result_map = {str(job.id): job for job in workspace_jobs}
        job_search_result_ids = list(job_search_result_map.keys())
        raw_hits = SemanticMatcher.compare(candidate_vector, limit=len(workspace_jobs), job_search_result_ids=job_search_result_ids)

        logger.info(f"[MatchingPipeline] Received {len(raw_hits)} semantic job matches for workspace {workspace_id}")

        # Chunk the raw hits into batches of 5
        batch_size = 5
        batches = [raw_hits[i:i + batch_size] for i in range(0, len(raw_hits), batch_size)]
        
        ranked_jobs = []
        updated_db_records = []

        import asyncio
        semaphore = asyncio.Semaphore(10)

        async def process_batch(batch_hits):
            async with semaphore:
                jobs_to_compare = []
                valid_hits = []
                for hit in batch_hits:
                    job_search_result_id = hit.get("payload", {}).get("job_search_result_id")
                    if not job_search_result_id:
                        continue
                    job_res = job_search_result_map.get(job_search_result_id)
                    if not job_res or not job_res.job_knowledge:
                        continue
                    jobs_to_compare.append(job_res.job_knowledge)
                    valid_hits.append((hit, job_res))

                if not jobs_to_compare:
                    return

                try:
                    # Phase 2: LLM Structured Comparison (Batched)
                    batch_result = await LLMComparisonService.compare_batch(candidate_semantic_doc, jobs_to_compare)
                    
                    # Create a map of results by job_knowledge_id
                    result_map = {res.job_id: res.comparison for res in batch_result.matches}
                    
                    # Phase 3: Deterministic Scoring
                    for hit, job_res in valid_hits:
                        jk_id = str(job_res.job_knowledge.id)
                        llm_comparison_result = result_map.get(jk_id)
                        
                        if not llm_comparison_result:
                            logger.warning(f"[MatchingPipeline] Missing LLM result for job {jk_id}")
                            continue

                        component_scores = DeterministicMatcher.calculate_component_scores(llm_comparison_result)
                        det_score = DeterministicMatcher.calculate_total_deterministic_score(component_scores)
                        
                        sem_score = hit.get("score", 0.0)
                        final_score = HybridMatcher.calculate_hybrid_score(sem_score, det_score)

                        # Build First-Class MatchKnowledge Schema
                        candidate_context = CandidateContext(
                            level=str(insight.artifact_json.get("candidate_level", {}).get("title", "Unknown")),
                            primary_domain=str(insight.artifact_json.get("candidate_identity", {}).get("engineering_profile", "Unknown")),
                            total_experience_months=int(insight.artifact_json.get("candidate_level", {}).get("total_months_experience", 0))
                        )
                        
                        match_knowledge = MatchKnowledge(
                            candidate_context=candidate_context,
                            semantic_score=sem_score,
                            structured_comparison=llm_comparison_result,
                            component_scores=component_scores,
                            final_score=final_score
                        )

                        job_res.semantic_score = sem_score
                        job_res.deterministic_score = det_score
                        job_res.final_score = final_score
                        
                        # Extract matching and missing skills for quick UI access
                        matched_req_skills = [sm.candidate_skill for sm in llm_comparison_result.matched_required_technologies if sm.candidate_skill]
                        matched_pref_skills = [sm.candidate_skill for sm in llm_comparison_result.matched_preferred_technologies if sm.candidate_skill]
                        job_res.matching_skills = matched_req_skills + matched_pref_skills
                        job_res.missing_skills = llm_comparison_result.missing_required_technologies
                        
                        job_res.comparison_evidence = match_knowledge.model_dump(mode="json")
                        updated_db_records.append(job_res)

                        ranked_jobs.append(
                            RankedJob(
                                job_search_result_id=job_res.id,
                                job_title=job_res.job_title,
                                company_name=job_res.company_name,
                                semantic_score=sem_score,
                                final_match_score=final_score
                            )
                        )
                except Exception as batch_err:
                    logger.error(f"[MatchingPipeline] Failed processing batch: {batch_err}")

        # Execute all batches concurrently
        tasks = [process_batch(batch) for batch in batches]
        await asyncio.gather(*tasks)

        # 5. Batch commit all updates to PostgreSQL
        if updated_db_records:
            try:
                db.commit()
                logger.info(f"[MatchingPipeline] Successfully batch persisted MatchKnowledge for {len(updated_db_records)} records.")
            except Exception as commit_err:
                db.rollback()
                logger.error(f"[MatchingPipeline] Failed to batch commit job score updates: {commit_err}")
                raise commit_err

        # 6. Sort results descending via RankingService
        ranked_list = RankingService.rank_jobs(ranked_jobs)
        logger.info(f"[MatchingPipeline] Completed hybrid ranking for workspace {workspace_id}.")
        return ranked_list
