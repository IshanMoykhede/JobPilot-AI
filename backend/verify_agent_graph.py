import asyncio
import os
import sys
from uuid import UUID

# Ensure we can import from the app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.core.database import SessionLocal
from app.agent.services.orchestration_service import OrchestrationService

# We'll need a mock candidate profile id. We assume one exists in the DB.
# Replace with a real UUID from your db if needed. For now, we will query the first available.

async def verify():
    db = SessionLocal()
    try:
        from app.models.candidate_profile import CandidateProfile
        from app.models.user import User  # Needed for relationship resolution
        
        # Get first candidate profile to use as mock
        candidate = db.query(CandidateProfile).first()
        if not candidate:
            print("No CandidateProfile found in database. Please ensure DB is seeded before testing.")
            return

        candidate_profile_id = candidate.id
        
        print(f"=== Testing JOB SEARCH Intent ===")
        user_query = "Find backend jobs in Pune"
        response = await OrchestrationService.run_graph(db, candidate_profile_id, user_query)
        print("\n[JOB SEARCH Response]")
        print(response)

        print("\n=== Testing GENERAL CHAT Intent ===")
        user_query = "Hello, how are you today?"
        response = await OrchestrationService.run_graph(db, candidate_profile_id, user_query)
        print("\n[GENERAL CHAT Response]")
        print(response)
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(verify())
