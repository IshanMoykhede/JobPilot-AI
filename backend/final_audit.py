import os
import random
import time
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.job_search.models.job_knowledge import JobKnowledge
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.models.search_workspace import SearchWorkspace
from app.models.candidate_profile import CandidateProfile
from app.conversation.models.conversation import Conversation
from app.models.user import User
from app.models.candidate_insights import CandidateInsights

from app.embedding.services.job_document_builder import JobDocumentBuilder

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run_audit():
    db = SessionLocal()
    
    workspace = db.query(SearchWorkspace).order_by(SearchWorkspace.created_at.desc()).first()
    if not workspace:
        print("No workspace found.")
        return
        
    print("=== STEP 1: PIPELINE COMPLETENESS ===")
    j_count = db.query(JobSearchResult).filter(JobSearchResult.workspace_id == workspace.id).count()
    jk_count = db.query(JobKnowledge).count()
    
    print(f"JobSearchResults created: {j_count}")
    print(f"JobKnowledge generated: {jk_count}")
    
    print("\n=== STEP 2: EXTRACTION QUALITY AUDIT (up to 15) ===")
    all_jks = db.query(JobKnowledge).all()
    sample = random.sample(all_jks, min(15, len(all_jks)))
    
    domains = {}
    for idx, jk in enumerate(sample):
        # find corresponding job result
        job = db.query(JobSearchResult).filter(JobSearchResult.job_knowledge_id == jk.id).first()
        raw_desc = job.raw_job_json.get("description", "")[:200] + "..." if job and job.raw_job_json else "No raw desc"
        
        domain_name = jk.primary_domain.value if hasattr(jk.primary_domain, 'value') else str(jk.primary_domain)
        domains[domain_name] = domains.get(domain_name, 0) + 1
        
        print(f"\n--- Record {idx+1}: {jk.job_title} ---")
        print(f"Raw Desc Snapshot: {raw_desc}")
        print(f"Primary Domain: {domain_name}")
        print(f"Technologies: {jk.technologies}")
        print(f"Capabilities: {jk.capabilities}")
        print(f"Responsibilities: {jk.responsibilities}")
        print(f"Must Have Requirements: {jk.must_have_requirements}")
        print(f"Preferred Requirements: {jk.preferred_requirements}")
        print(f"Semantic Summary: {jk.semantic_summary}")

    print("\n=== STEP 3: CROSS DOMAIN VALIDATION ===")
    for domain, count in domains.items():
        print(f"{domain}: {count}")

    print("\n=== STEP 4: DOCUMENT QUALITY ===")
    for idx, jk in enumerate(sample[:10]):
        doc = JobDocumentBuilder.build_document(jk)
        print(f"\n--- Document {idx+1} ---")
        print(doc[:300] + "...\n[TRUNCATED]")

    print("\n=== STEP 5: RECOMMENDATION QUALITY ===")
    jobs = db.query(JobSearchResult).filter(
        JobSearchResult.workspace_id == workspace.id,
        JobSearchResult.final_score.isnot(None)
    ).order_by(JobSearchResult.final_score.desc()).limit(10).all()
    
    for i, job in enumerate(jobs, 1):
        print(f"[{i}] {job.job_title}")
        print(f"Semantic Score: {job.semantic_score}")
        print(f"Deterministic Score: {job.deterministic_score}")
        print(f"Hybrid Score: {job.final_score}")
        
    print("\n=== STEP 6: PERFORMANCE ===")
    print(f"Workspace duration: {workspace.processing_duration}s")
    if workspace.search_metadata:
        print(f"Provider Latency: {workspace.search_metadata.get('provider_latency')}s")
        
    db.close()

if __name__ == "__main__":
    run_audit()
