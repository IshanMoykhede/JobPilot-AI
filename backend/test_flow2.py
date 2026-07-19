import asyncio
from app.core.database import SessionLocal
from app.agent.services.orchestration_service import OrchestrationService
from uuid import UUID

# Import all models to prevent SQLAlchemy mapper errors
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_insights import CandidateInsights
from app.conversation.models.conversation import Conversation
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.models.job_knowledge import JobKnowledge

async def main():
    db = SessionLocal()
    user = db.query(User).first()
    if not user:
        print("No user found")
        return
        
    print(f"Using user {user.email}")
    if not user.candidate_profile:
        print("No candidate profile")
        return
        
    try:
        final_state = await OrchestrationService.run_graph(
            db=db,
            candidate_profile_id=user.candidate_profile.id,
            user_query="AI Engineer job openings",
            user_id=user.id
        )
        print(final_state.get("workspace_id"))
        print("SUCCESS!")
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    asyncio.run(main())
