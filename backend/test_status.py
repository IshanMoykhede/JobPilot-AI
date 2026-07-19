import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.agent.services.orchestration_service import OrchestrationService
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult
from collections import Counter

logging.basicConfig(level=logging.INFO)

db = SessionLocal()
workspace = db.query(SearchWorkspace).order_by(SearchWorkspace.created_at.desc()).first()
print(f"Latest Workspace ID: {workspace.id}")

workspace_jobs = db.query(JobSearchResult).filter(JobSearchResult.workspace_id == workspace.id).all()
print(f"Total Jobs in workspace: {len(workspace_jobs)}")

statuses = Counter([job.processing_status for job in workspace_jobs])
print("Statuses:")
for status, count in statuses.items():
    print(f"  {status}: {count}")

null_scores = sum(1 for j in workspace_jobs if j.final_score is None)
print(f"Jobs with final_score IS NULL: {null_scores}")
