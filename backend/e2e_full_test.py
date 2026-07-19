import asyncio
import time
from uuid import uuid4
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.candidate_profile import CandidateProfile
from app.agent.nodes.job_search_node import job_search_node
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.models.job_knowledge import JobKnowledge

async def main_func():
    db = SessionLocal()
    candidate = db.query(CandidateProfile).first()
    if not candidate:
        print("No candidate found!")
        return

    query = "Backend Developer Internship Pune"
    print(f"Executing End-to-End Pipeline for query: {query}")
    
    state = {
        "messages": [],
        "user_query": query,
        "candidate_profile_id": str(candidate.id)
    }
    
    start_time = time.time()
    try:
        new_state = await job_search_node(state)
        print("Pipeline Execution Completed.")
    except Exception as e:
        print(f"Pipeline crashed: {e}")
        return
        
    duration = time.time() - start_time
    
    # Assertions and Report
    w = db.query(SearchWorkspace).order_by(SearchWorkspace.created_at.desc()).first()
    
    results = db.query(JobSearchResult).filter_by(workspace_id=w.id).all()
    knowledge_records = db.query(JobKnowledge).filter(JobKnowledge.id.in_([r.job_knowledge_id for r in results if r.job_knowledge_id])).all()
    print("\n=======================================================")
    print("FINAL VERIFICATION REPORT")
    print("=======================================================")
    print(f"1. Number of jobs retrieved: {len(results)}")
    print(f"2. Number of JobKnowledge records created: {len(knowledge_records)}")
    print(f"3. Number of Groq 429 retries: (Check logs for 'Groq returned HTTP 429')")
    print(f"4. Total processing duration: {duration:.2f} seconds")
    print("\n5. Final Confirmation:")
    print(f"   Jobs Retrieved ({len(results)}) == JobKnowledge ({len(knowledge_records)})")
    
    if len(results) == len(knowledge_records) and len(results) > 0:
        print("   ✅ PIPELINE GUARANTEE SATISFIED.")
    else:
        print("   ❌ PIPELINE GUARANTEE FAILED.")

if __name__ == "__main__":
    import main
    asyncio.run(main_func())
