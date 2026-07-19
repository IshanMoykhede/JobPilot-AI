import os
import sys
import logging

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, engine
from app.core.config import settings
from qdrant_client import QdrantClient
from app.vector_store.core import vector_store_config

from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_insights import CandidateInsights
from app.conversation.models.conversation import Conversation
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.models.job_knowledge import JobKnowledge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    logger.info("Dropping all PostgreSQL tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Recreating all PostgreSQL tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("PostgreSQL database reset complete.")
    
    logger.info("Connecting to Qdrant...")
    try:
        qdrant = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        for collection in [vector_store_config.CANDIDATE_COLLECTION, vector_store_config.JOB_COLLECTION]:
            if qdrant.collection_exists(collection):
                qdrant.delete_collection(collection)
                logger.info(f"Deleted Qdrant collection: {collection}")
            else:
                logger.info(f"Qdrant collection {collection} does not exist. Skipping.")
        logger.info("Qdrant reset complete.")
    except Exception as e:
        logger.error(f"Failed to reset Qdrant: {e}")

if __name__ == "__main__":
    confirm = input("WARNING: This will delete ALL data in PostgreSQL and Qdrant.\nType 'yes' to continue: ")
    if confirm.lower() == 'yes':
        reset_database()
        print("System reset successful.")
    else:
        print("Aborted.")
