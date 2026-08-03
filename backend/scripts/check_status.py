import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.conversation.models.conversation import Conversation
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.models.job_knowledge import JobKnowledge
from app.vector_store.services.vector_store_service import VectorStoreService

def check():
    db = SessionLocal()
    workspace = db.query(SearchWorkspace).order_by(SearchWorkspace.created_at.desc()).first()
    if not workspace:
        print("No workspace found")
        return
        
    print(f"Latest Workspace: {workspace.id}")
    
    jobs = db.query(JobSearchResult).filter(JobSearchResult.workspace_id == workspace.id).all()
    print(f"Jobs in DB for this workspace: {len(jobs)}")
    
    for job in jobs[:10]:
        print(f"  Job {job.id} | Status: {job.processing_status} | Final Score: {job.final_score}")
        
    # Check Qdrant
    points = VectorStoreService.search(
        collection_name="job_embeddings",
        query_vector=[0.1] * 384,
        limit=100,
        filter_dict={"workspace_id": [str(workspace.id)]}
    )
    print(f"Jobs in Qdrant for this workspace: {len(points)}")
    
    # Check Qdrant using job_search_result_id filter
    job_ids = [str(j.id) for j in jobs]
    if job_ids:
        points_by_job_id = VectorStoreService.search(
            collection_name="job_embeddings",
            query_vector=[0.1] * 384,
            limit=100,
            filter_dict={"job_search_result_id": job_ids}
        )
        print(f"Jobs in Qdrant using job_id filter: {len(points_by_job_id)}")
    
if __name__ == "__main__":
    check()
