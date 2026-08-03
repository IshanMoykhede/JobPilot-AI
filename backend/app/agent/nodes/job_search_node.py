import logging
from app.agent.schemas.agent_state import AgentState

# Import existing subsystems
from app.job_search.services.retrieval_pipeline_service import RetrievalPipelineService
from app.job_search.services.job_knowledge_engine import JobKnowledgeEngine
from app.embedding.services.embedding_pipeline import EmbeddingGenerationPipeline
from app.job_search_agent.matching.services.matching_pipeline import MatchingPipeline
from app.job_search_agent.explanation.services.explanation_pipeline import ExplanationPipeline

logger = logging.getLogger(__name__)

from app.core.database import SessionLocal

async def job_search_node(state: AgentState) -> dict:
    """
    Orchestrates the Sprints 2-6 Job Search pipelines.
    Contains no business logic, simply delegates to existing modules.
    """
    logger.info("[JobSearchNode] Started execution.")
    candidate_profile_id = state["candidate_profile_id"]
    original_query = state["user_query"]
    conversation_id = state.get("conversation_id")

    with SessionLocal() as db:
        try:
            # 1. Retrieval (Sprint 2)
            print(f"\n[{'='*50}]")
            print("--> ENTERING PIPELINE: RETRIEVAL")
            logger.info("[JobSearchNode] Invoking RetrievalPipelineService...")
            retrieval_result = await RetrievalPipelineService.execute_pipeline(
                db=db,
                candidate_profile_id=candidate_profile_id,
                original_query=original_query,
                conversation_id=conversation_id
            )
            workspace_id = retrieval_result["workspace_id"]
            conv_id = retrieval_result["conversation_id"]

            # 2. Job Knowledge Generation (Sprint 3)
            print(f"\n[{'='*50}]")
            print("--> ENTERING PIPELINE: JOB KNOWLEDGE GENERATION")
            logger.info("[JobSearchNode] Invoking JobKnowledgeEngine...")
            await JobKnowledgeEngine.generate_job_knowledge_for_workspace(db, workspace_id)
            db.commit()  # Force transaction end to see task_db commits from background jobs

            # 3. Job Embedding Generation (Sprint 4)
            print(f"\n[{'='*50}]")
            print("--> ENTERING PIPELINE: EMBEDDING GENERATION")
            logger.info("[JobSearchNode] Invoking EmbeddingGenerationPipeline...")
            await EmbeddingGenerationPipeline.generate_job_embeddings_for_workspace(db, workspace_id)
            db.commit()  # Force transaction end

            # 4. Semantic & Deterministic Matching (Sprint 5)
            print(f"\n[{'='*50}]")
            print("--> ENTERING PIPELINE: HYBRID MATCHING")
            logger.info("[JobSearchNode] Invoking MatchingPipeline...")
            ranked_jobs = await MatchingPipeline.run_matching_pipeline(db, candidate_profile_id, workspace_id)

            # We need candidate_knowledge for the explanation pipeline (from matching context)
            # We can extract it from the database since it's already generated.
            from app.models.candidate_insights import CandidateInsights, ArtifactType, InsightStatus
            insight = db.query(CandidateInsights).filter(
                CandidateInsights.candidate_profile_id == candidate_profile_id,
                CandidateInsights.artifact_type == ArtifactType.CANDIDATE_KNOWLEDGE,
                CandidateInsights.status == InsightStatus.COMPLETED
            ).first()
            
            candidate_knowledge = insight.artifact_json if insight else {}

            # 5. LLM Explanation (Sprint 6)
            print(f"\n[{'='*50}]")
            print("--> ENTERING PIPELINE: LLM EXPLANATION GENERATION")
            logger.info("[JobSearchNode] Invoking ExplanationPipeline...")
            explanations = await ExplanationPipeline.run(db, ranked_jobs, conv_id)

            print(f"\n[{'='*50}]")
            print("--> GRAPH EXECUTION COMPLETED")
            print(f"[{'='*50}]\n")
            logger.info("[JobSearchNode] Completed successfully.")
            
            # Save response in state
            return {
                "conversation_id": conv_id,
                "workspace_id": workspace_id,
                "explanations": explanations,
                "response": {
                    "status": "SUCCESS",
                    "message": "Orchestration complete."
                }
            }

        except Exception as e:
            logger.error(f"[JobSearchNode] Pipeline failed: {e}")
            raise e
