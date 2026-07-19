import logging
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny

load_dotenv()
logging.basicConfig(level=logging.INFO)

import app.models.all_models
db = SessionLocal()
workspace = db.query(SearchWorkspace).order_by(SearchWorkspace.created_at.desc()).first()
print(f"Latest Workspace ID: {workspace.id}")

workspace_jobs = db.query(JobSearchResult).filter(JobSearchResult.workspace_id == workspace.id).all()
print(f"Jobs in workspace: {len(workspace_jobs)}")
job_ids = [str(job.id) for job in workspace_jobs]

url = os.getenv("QDRANT_URL")
api_key = os.getenv("QDRANT_API_KEY")
client = QdrantClient(url=url, api_key=api_key, timeout=10.0)

res = client.scroll(
    collection_name="job_vectors",
    scroll_filter=Filter(
        must=[
            FieldCondition(key="job_search_result_id", match=MatchAny(any=job_ids))
        ]
    ),
    limit=100
)
points = res[0]
print(f"Qdrant points for this workspace: {len(points)}")

for p in points[:3]:
    print(p.id)
