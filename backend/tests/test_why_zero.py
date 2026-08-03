from app.agent.services.orchestration_service import OrchestrationService
import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.models.search_workspace import SearchWorkspace
from app.vector_store.services.vector_store_service import VectorStoreService
from app.vector_store.core import vector_store_config
from app.job_search_agent.matching.services.semantic_matcher import SemanticMatcher
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

db = SessionLocal()
workspace = db.query(SearchWorkspace).order_by(SearchWorkspace.created_at.desc()).first()
print(f"Latest Workspace ID: {workspace.id}")

workspace_jobs = db.query(JobSearchResult).filter(JobSearchResult.workspace_id == workspace.id).all()
print(f"Jobs in workspace: {len(workspace_jobs)}")

job_ids = [str(job.id) for job in workspace_jobs]
print(f"Sample Job IDs: {job_ids[:3]}")

# Try direct Qdrant search with these IDs
matches = VectorStoreService.search(
    collection_name=vector_store_config.JOB_COLLECTION,
    query_vector=[0.1] * 384,
    limit=50,
    filter_dict={"job_search_result_id": job_ids}
)
print(f"Direct Search returned {len(matches)} matches")

# What are the processing statuses of these jobs?
from collections import Counter
statuses = Counter([job.processing_status.value for job in workspace_jobs])
print(f"Processing Statuses: {statuses}")
