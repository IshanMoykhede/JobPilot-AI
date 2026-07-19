import logging
from app.agent.schemas.agent_state import AgentState
from app.core.database import SessionLocal
from app.conversation.models.conversation import Conversation
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.models.search_workspace import ProcessingStatus

logger = logging.getLogger(__name__)

async def followup_node(state: AgentState) -> dict:
    logger.info("[FollowupNode] Started execution.")
    user_query = state.get("user_query")
    conversation_id = state.get("conversation_id")

    if not conversation_id:
        return {
            "response": {
                "status": "ERROR",
                "message": "No active conversation found for a follow-up query."
            }
        }

    with SessionLocal() as db:
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conv or not conv.active_workspace_id:
            return {
                "response": {
                    "status": "ERROR",
                    "message": "No active job search workspace found to follow up on."
                }
            }

        workspace_id = conv.active_workspace_id
        logger.info(f"[FollowupNode] Found active workspace: {workspace_id}")

        # Fetch top jobs for this workspace
        jobs = db.query(JobSearchResult).filter(
            JobSearchResult.workspace_id == workspace_id,
            JobSearchResult.processing_status == ProcessingStatus.KNOWLEDGE_GENERATED # or embedded
        ).order_by(JobSearchResult.final_score.desc()).limit(5).all()

        if not jobs:
             return {
                "response": {
                    "status": "SUCCESS",
                    "message": "The active workspace has no processed jobs yet."
                }
            }

        # Here we would use an LLM to answer the specific query using the jobs as context.
        # For the prototype, we simply return the top jobs to the user as context.
        return {
            "conversation_id": conversation_id,
            "workspace_id": workspace_id,
            "response": {
                "status": "SUCCESS",
                "message": f"Retrieved context from active workspace. Here are the top jobs for your follow-up.",
                "jobs": [
                    {
                        "job_title": j.job_title,
                        "company_name": j.company_name,
                        "match_score": j.final_score
                    } for j in jobs
                ]
            }
        }
