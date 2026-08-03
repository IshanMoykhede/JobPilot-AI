import asyncio
from uuid import uuid4
from app.core.database import SessionLocal
from app.agent.services.orchestration_service import OrchestrationService
from app.models.user import User
from app.models.candidate_profile import CandidateProfile

async def run_test():
    db = SessionLocal()
    
    # Get any valid candidate profile
    profile = db.query(CandidateProfile).first()
    if not profile:
        print("No candidate profile found.")
        return
        
    print(f"Using profile: {profile.id}")
    
    # 1. Initial Job Search
    print("\n--- Sending initial job search query ---")
    query_1 = "Find me a remote backend developer job."
    result_1 = await OrchestrationService.run_graph(
        db=db,
        candidate_profile_id=profile.id,
        user_query=query_1,
        user_id=profile.user_id,
        conversation_id=None
    )
    
    print(result_1)
    
    conv_id = result_1.get("conversation_id")
    print(f"\nCreated Conversation ID: {conv_id}")
    
    if not conv_id:
        print("No conversation ID returned!")
        return
        
    # 2. Follow-up query
    print("\n--- Sending follow-up query ---")
    query_2 = "Can you show me more details about the first job?"
    result_2 = await OrchestrationService.run_graph(
        db=db,
        candidate_profile_id=profile.id,
        user_query=query_2,
        user_id=profile.user_id,
        conversation_id=conv_id
    )
    
    print(result_2)
    
if __name__ == "__main__":
    asyncio.run(run_test())
