import asyncio
import os
import sys

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app  # This forces all models to be registered correctly
from app.core.database import SessionLocal
from app.job_search.models.search_workspace import SearchWorkspace
from app.conversation.models.conversation import Conversation
from app.embedding.services.embedding_pipeline import EmbeddingGenerationPipeline
from app.models.candidate_insights import CandidateInsights
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def regenerate():
    db = SessionLocal()
    try:
        # Get the first candidate insight
        insight = db.query(CandidateInsights).first()
        if not insight:
            logger.error("No candidate insight found.")
            return
            
        logger.info(f"Regenerating embeddings for insight ID: {insight.id}")
        
        await EmbeddingGenerationPipeline.generate_candidate_embedding(db, insight.id)
        
        logger.info("Successfully regenerated and pushed candidate embedding to Qdrant!")
    except Exception as e:
        logger.error(f"Error regenerating: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(regenerate())
