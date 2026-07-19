import os
import asyncio
import uuid
import hashlib
from dotenv import load_dotenv

# Load env variables from project root
load_dotenv(os.path.join(os.getcwd(), '.env'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.database import SessionLocal
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.job_search.models.search_workspace import SearchWorkspace, ProcessingStatus
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.models.job_knowledge import JobKnowledge
from app.job_search.core.job_enums import JobProcessingStatus
from app.job_search.services.retrieval_pipeline_service import RetrievalPipelineService
from app.job_search.services.job_knowledge_engine import JobKnowledgeEngine
from app.agent.schemas.agent_state import AgentState

async def main():
    db = SessionLocal()
    
    # 1. Ensure mock CandidateProfile exists for user '5a78cc85-0b93-4332-8bee-f1f924f1c01a'
    user = db.query(User).filter_by(id='5a78cc85-0b93-4332-8bee-f1f924f1c01a').first()
    if not user:
        print("Creating mock user...")
        user = User(
            id=uuid.UUID('5a78cc85-0b93-4332-8bee-f1f924f1c01a'),
            email='moykhedeishan@gmail.com',
            name='Ishan Moykhede'
        )
        db.add(user)
        db.commit()
        
    profile = db.query(CandidateProfile).filter_by(user_id=user.id).first()
    if not profile:
        print("Creating mock candidate profile...")
        profile = CandidateProfile(
            id=uuid.uuid4(),
            user_id=user.id,
            onboarding_completed=True,
            profile_json={}
        )
        db.add(profile)
        db.commit()
    
    # Clean previous workspace and jobs to make verification clean
    print("Cleaning database tables for clean test...")
    db.query(JobSearchResult).delete()
    db.query(JobKnowledge).delete()
    db.query(SearchWorkspace).delete()
    db.commit()
    
    # Run Retrieval
    original_query = "Backend Developer job openings in Pune"
    print(f"Executing Retrieval pipeline for: {original_query}")
    
    # Capture SerpAPI details
    # To capture SerpAPI parameters and response, we will temporarily hook or log.
    # Actually, RetrievalPipelineService calls SerpService().search_jobs.
    # Let's execute and retrieve results from the database.
    try:
        retrieval_res = await RetrievalPipelineService.execute_pipeline(
            db=db,
            candidate_profile_id=profile.id,
            original_query=original_query
        )
        workspace_id = retrieval_res['workspace_id']
        conversation_id = retrieval_res['conversation_id']
        print(f"Retrieval Succeeded: workspace_id={workspace_id}")
    except Exception as e:
        print(f"Retrieval Failed: {e}")
        return

    # Check Workspace row
    workspace = db.query(SearchWorkspace).filter_by(id=workspace_id).first()
    print("\n--- SearchWorkspace Row ---")
    print(f"ID: {workspace.id}")
    print(f"Original Query: {workspace.original_query}")
    print(f"Optimized Query: {workspace.optimized_query}")
    print(f"Total Jobs Fetched: {workspace.total_jobs_fetched}")
    print(f"Status: {workspace.processing_status}")
    print(f"Metadata: {workspace.search_metadata}")
    
    # RawJobs persisted
    raw_jobs = db.query(JobSearchResult).filter_by(workspace_id=workspace_id).all()
    print(f"\nFetched {len(raw_jobs)} raw jobs from DB.")
    for idx, rj in enumerate(raw_jobs):
        print(f"Job {idx+1}: DB_ID={rj.id}, Provider_ID={rj.provider_job_id}, Title={rj.job_title}, Company={rj.company_name}, Location={rj.location}, Status={rj.processing_status}, JK_ID={rj.job_knowledge_id}")
        
    # State before entering pipeline 2
    messages = [{"role": "user", "content": original_query}]
    state_before: AgentState = {
        "conversation_id": conversation_id,
        "workspace_id": workspace_id,
        "candidate_profile_id": profile.id,
        "user_query": original_query,
        "intent": "job_search",
        "messages": messages,
        "response": None,
        "explanations": None,
        "metadata": {}
    }
    print("\nState before Pipeline 2:", state_before)
    
    # Run Job Knowledge Pipeline
    print("\nExecuting Job Knowledge Pipeline...")
    # We will run the generator step-by-step or trace it. Let's trace it by looking at DB changes.
    # To demonstrate caching, let's run it once. Since DB was cleared, it will be all cache misses.
    # Then we run it again for verification of cache hits!
    
    # First pass: All cache misses
    await JobKnowledgeEngine.generate_job_knowledge_for_workspace(db, workspace_id)
    db.commit()
    
    print("\nChecking JobKnowledge extraction results...")
    processed_jobs = db.query(JobSearchResult).filter_by(workspace_id=workspace_id).all()
    for idx, pj in enumerate(processed_jobs):
        desc = pj.raw_job_json.get("description", "") if pj.raw_job_json else ""
        raw_string = f"{pj.job_title}:{pj.company_name or 'Unknown'}:{desc}"
        job_hash = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()
        jk = db.query(JobKnowledge).filter_by(id=pj.job_knowledge_id).first()
        print(f"Job {idx+1}: DB_ID={pj.id}, Title={pj.job_title}, Hash={job_hash}, JK_ID={pj.job_knowledge_id}, ProcessingStatus={pj.processing_status}")
        if jk:
            print(f"   JK details -> Domain={jk.primary_domain}, Techs={jk.technologies}, Caps={jk.capabilities}")
            
    # Now let's trigger a second workspace run to verify cache hits!
    # We create a new workspace with the same user, but we inject duplicate/same job results to trigger cache hits.
    print("\nCreating a duplicate workspace to test caching...")
    dup_workspace = SearchWorkspace(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        candidate_profile_id=profile.id,
        original_query="Same query",
        optimized_query="Same role",
        processing_status=ProcessingStatus.RAW_JOBS_READY
    )
    db.add(dup_workspace)
    db.flush()
    
    # Re-insert the same jobs under the new workspace
    for rj in raw_jobs:
        dup_job = JobSearchResult(
            id=uuid.uuid4(),
            workspace_id=dup_workspace.id,
            provider_job_id=rj.provider_job_id + "_dup",
            job_title=rj.job_title,
            company_name=rj.company_name,
            location=rj.location,
            raw_job_json=rj.raw_job_json,
            processing_status=JobProcessingStatus.RAW
        )
        db.add(dup_job)
    db.commit()
    
    # Process duplicate workspace knowledge
    print("Generating Job Knowledge for duplicate workspace (should trigger CACHE HITS)...")
    await JobKnowledgeEngine.generate_job_knowledge_for_workspace(db, dup_workspace.id)
    db.commit()
    
    # Inspect duplicate workspace job results
    dup_processed_jobs = db.query(JobSearchResult).filter_by(workspace_id=dup_workspace.id).all()
    print("\n--- Duplicate Workspace (Cache Hit Verification) ---")
    for idx, dpj in enumerate(dup_processed_jobs):
        print(f"Dup Job {idx+1}: Title={dpj.job_title}, JK_ID={dpj.job_knowledge_id}, ProcessingStatus={dpj.processing_status}")
        
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
