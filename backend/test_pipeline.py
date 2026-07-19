import asyncio
import logging
from uuid import UUID
from app.core.database import SessionLocal
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.agent.services.orchestration_service import OrchestrationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PipelineTest")

async def test_pipeline():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user or not user.candidate_profile:
            logger.error("No suitable user found with a candidate profile.")
            return

        candidate_profile_id = user.candidate_profile.id
        user_query = "AI engineer internship openings in Pune and Bangalore"
        
        logger.info(f"Running pipeline for candidate: {candidate_profile_id}")
        
        # This will trigger the intent router, then the job search pipeline
        final_state = await OrchestrationService.run_graph(
            db=db,
            candidate_profile_id=candidate_profile_id,
            user_id=user.id,
            user_query=user_query,
            conversation_id=None
        )
        
        logger.info("Pipeline completed.")
        
        workspace_id = final_state.get("workspace_id")
        if workspace_id:
            from app.presentation.job_search_presentation_builder import JobSearchPresentationBuilder
            response_dto = JobSearchPresentationBuilder.build_response(
                db=db,
                workspace_id=workspace_id,
                explanations=final_state.get("explanations", [])
            )
            
            payload = response_dto.model_dump()
            import json
            logger.info("================= RESULTS =================")
            logger.info(json.dumps(payload, indent=2))
            logger.info("==========================================")
        else:
            logger.error("No workspace_id returned from pipeline.")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_pipeline())
