from app.core.database import SessionLocal
from app.conversation.models.conversation import Conversation
from app.conversation.models.conversation_message import ConversationMessage
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.models.job_knowledge import JobKnowledge

db = SessionLocal()
w = db.query(SearchWorkspace).order_by(SearchWorkspace.created_at.desc()).first()
print('Workspace ID:', w.id)
print('Original Query:', w.original_query)
print('Optimized Query:', w.optimized_query)
print('Total Fetched:', w.total_jobs_fetched)

results = db.query(JobSearchResult).filter_by(workspace_id=w.id).all()
for r in results:
    raw_source = r.raw_job_json.get("source", "unknown") if r.raw_job_json else "none"
    print(f'Job ID: {r.id} | Source: {r.source} | Raw Provider: {raw_source} | Status: {r.processing_status.value if r.processing_status else "None"} | Final Score: {r.final_score}')
    if r.raw_job_json:
        print(f"Raw Title: {r.raw_job_json.get('title')} | Raw Location: {r.raw_job_json.get('location')}")
