from app.core.database import SessionLocal
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult

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
