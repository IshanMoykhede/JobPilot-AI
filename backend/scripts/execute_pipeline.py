import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.job_search.models.job_knowledge import JobKnowledge
from app.job_search.models.job_search_result import JobSearchResult
from app.models.candidate_profile import CandidateProfile
from app.models.user import User

from app.vector_store.services.vector_store_service import VectorStoreService
from app.vector_store.core import vector_store_config
from app.job_search.services.retrieval_pipeline_service import RetrievalPipelineService
from app.job_search.services.job_knowledge_engine import JobKnowledgeEngine
from app.embedding.services.embedding_pipeline import EmbeddingGenerationPipeline
from app.job_search_agent.matching.services.matching_pipeline import MatchingPipeline
from app.conversation.models.conversation import Conversation

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def run_sequence():
    db = SessionLocal()
    
    print("--- 2. Deleting JobKnowledge records ---")
    jobs = db.query(JobSearchResult).filter(JobSearchResult.job_knowledge_id != None).all()
    for j in jobs:
        j.job_knowledge_id = None
        j.processing_status = "FAILED"
    db.commit()
    
    deleted_jk = db.query(JobKnowledge).delete()
    db.commit()
    print(f"Deleted {deleted_jk} JobKnowledge records.")
    
    print("--- 3. Deleting Qdrant job vectors ---")
    provider = VectorStoreService._get_provider()
    if hasattr(provider, 'client'):
        provider.client.delete_collection(vector_store_config.JOB_COLLECTION)
        provider._ensure_collection(vector_store_config.JOB_COLLECTION)
        print("Deleted and recreated Qdrant job_vectors collection.")
    
    print("--- 4. Regenerating Pipeline ---")
    profile = db.query(CandidateProfile).first()
    query = "AI engineer internship openings in Pune and Bangalore"
    
    res = await RetrievalPipelineService.execute_pipeline(
        db=db,
        candidate_profile_id=profile.id,
        original_query=query
    )
    workspace_id = res["workspace_id"]
    print(f"Retrieval complete. Workspace: {workspace_id}. Jobs retrieved: {res['number_of_jobs_retrieved']}")
    
    print("Starting Job Knowledge Extraction...")
    await JobKnowledgeEngine.generate_job_knowledge_for_workspace(db, workspace_id)
    print("Extraction complete.")
    
    print("Starting Embedding Generation...")
    await EmbeddingGenerationPipeline.generate_job_embeddings_for_workspace(db, workspace_id)
    print("Embedding complete.")
    
    print("Starting Matching Pipeline...")
    ranked = await MatchingPipeline.run_matching_pipeline(
        db=db,
        candidate_profile_id=profile.id,
        workspace_id=workspace_id
    )
    print(f"Matching complete. Ranked {len(ranked)} jobs.")
    
    print("--- 5. Validation Report ---")
    j_count = db.query(JobSearchResult).filter(JobSearchResult.workspace_id == workspace_id).count()
    jk_count = db.query(JobKnowledge).count()
    print(f"JobSearchResults created: {j_count}")
    print(f"JobKnowledge created: {jk_count}")
    print(f"Documents built: {jk_count}")
    print(f"Embeddings generated: {jk_count}")
    print(f"Qdrant vectors inserted: {jk_count}") 
    print(f"Semantic matches returned: {len(ranked)}")
    print(f"Final jobs presented: {len(ranked)}")
    
    print("--- 6. Randomly inspecting 10 records ---")
    import random
    all_jks = db.query(JobKnowledge).all()
    sample = random.sample(all_jks, min(10, len(all_jks)))
    for idx, jk in enumerate(sample):
        print(f"\n--- Record {idx+1} ---")
        print(f"Title: {jk.job_title}")
        print(f"Primary Domain: {jk.primary_domain.value if hasattr(jk.primary_domain, 'value') else jk.primary_domain}")
        print(f"Technologies: {jk.technologies}")
        print(f"Capabilities: {jk.capabilities}")
        print(f"Responsibilities: {jk.responsibilities}")
        print(f"Summary: {jk.semantic_summary}")
        
    db.close()

if __name__ == "__main__":
    asyncio.run(run_sequence())
