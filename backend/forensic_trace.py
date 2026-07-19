from app.core.database import SessionLocal
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult
from app.conversation.models.conversation import Conversation
import json

db = SessionLocal()
workspace = db.query(SearchWorkspace).order_by(SearchWorkspace.created_at.desc()).first()
if workspace:
    print('Workspace ID:', workspace.id)
    print('Original Query:', workspace.original_query)
    print('Optimized Query:', workspace.optimized_query)
    print('Total Fetched:', workspace.total_jobs_fetched)
    
    results = db.query(JobSearchResult).filter_by(workspace_id=workspace.id).all()
    print('Jobs Retrieved:', len(results))
    for r in results:
        raw_source = r.raw_job_json.get("source", "unknown") if r.raw_job_json else "none"
        print(f' - Job: {r.job_title} | Source DB: {r.source} | Source Raw: {raw_source} | Status: {r.processing_status.value if r.processing_status else None}')
        
    conv = db.query(Conversation).filter_by(id=workspace.conversation_id).first()
    if conv:
        msgs = conv.messages[-3:]
        for m in msgs:
            print(f'Role: {m.role}, Type: {m.message_type}')
            # print content but truncate if too long
            content_str = str(m.content)
            print(f'Content: {content_str[:500]}...')
