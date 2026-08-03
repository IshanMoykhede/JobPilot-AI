import requests
import time
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.conversation.models.conversation import Conversation
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.models.job_knowledge import JobKnowledge

# 1. Hit the /agent/chat endpoint
print("Sending query to /agent/chat...")
response = requests.post(
    "http://127.0.0.1:8000/agent/chat",
    json={"query": "Backend Developer Internship Pune"}
)

data = response.json()
print("Response received.")

db = SessionLocal()
w = db.query(SearchWorkspace).filter(SearchWorkspace.original_query == "Backend Developer Internship Pune").order_by(SearchWorkspace.created_at.desc()).first()
if not w:
    print("Workspace not found!")
    exit(1)

print("\n--- Validation Report ---")
print(f"1. Query received from frontend: {w.original_query}")
print(f"2. Exact payload sent to SerpAPI (optimized_query): {w.optimized_query}")

results = db.query(JobSearchResult).filter_by(workspace_id=w.id).all()
print(f"3. Number of jobs returned (raw fetched): {w.total_jobs_fetched}")
print(f"4. Number of JobSearchResults created: {len(results)}")

knowledge_records = db.query(JobKnowledge).filter(JobKnowledge.id.in_([r.job_knowledge_id for r in results if r.job_knowledge_id])).all()
print(f"5. Number of JobKnowledge records generated: {len(knowledge_records)}")

print(f"6. Number of Qdrant vectors total in collection: (Skipped)")

payload_jobs = data.get("payload", {}).get("jobs", []) if isinstance(data, dict) and "payload" in data else []
print(f"7. Number of jobs returned to the frontend: {len(payload_jobs)}")

# Print exact SerpAPI provider metadata
metadata = w.search_metadata or {}
print(f"8. Provider used: {metadata.get('provider')}")
print(f"9. Jobs received by provider: {metadata.get('jobs_received')}")
print(f"10. Provider status: {metadata.get('provider_status')}")

