import asyncio
import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app # Load all models
from app.core.database import SessionLocal
from app.agent.nodes.job_search_node import job_search_node
from app.models.candidate_profile import CandidateProfile

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("search_debug_validation.log", mode="w"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def run_test():
    db = SessionLocal()
    try:
        # Get the first candidate profile
        profile = db.query(CandidateProfile).first()
        if not profile:
            logger.error("No candidate profile found.")
            return

        logger.info(f"Starting test for candidate: {profile.id}")
        
        state = {
            "candidate_profile_id": profile.id,
            "user_query": "AI engineer internship openings in Pune and Bangalore",
            "conversation_id": None
        }

        # Run the node
        result = await job_search_node(state)
        logger.info(f"Final Result returned from job_search_node.")

    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_test())
