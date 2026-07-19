import logging
from app.vector_store.services.vector_store_service import VectorStoreService
from app.vector_store.core import vector_store_config
from app.core.database import SessionLocal
from app.job_search.models.job_search_result import JobSearchResult

logging.basicConfig(level=logging.INFO)

db = SessionLocal()
workspace_jobs = db.query(JobSearchResult).all()
print(f"Total jobs in DB: {len(workspace_jobs)}")
ids = [str(j.id) for j in workspace_jobs][-10:] # last 10
print(f"Testing filter with IDs: {ids}")

matches = VectorStoreService.search(
    collection_name=vector_store_config.JOB_COLLECTION,
    query_vector=[0.1] * 768,  # dummy vector
    limit=10,
    filter_dict={"job_search_result_id": ids}
)
print(f"Matches: {matches}")
