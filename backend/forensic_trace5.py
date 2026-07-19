from app.core.database import SessionLocal
from app.conversation.models.conversation import Conversation
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult
import json
db = SessionLocal()
w = db.query(SearchWorkspace).order_by(SearchWorkspace.created_at.desc()).first()
results = db.query(JobSearchResult).filter_by(workspace_id=w.id).all()
for r in results:
    print(f'Job ID: {r.id}')
    if r.raw_job_json:
        print('  Provider:', r.raw_job_json.get('provider', 'N/A'))
        print('  Source string:', r.raw_job_json.get('source', 'N/A'))
    else:
        print('  No raw JSON')
