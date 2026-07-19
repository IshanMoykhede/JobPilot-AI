import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.models.job_knowledge import JobKnowledge
from app.matching.core import matching_config
from app.conversation.models.conversation import Conversation
from app.models.candidate_profile import CandidateProfile
from app.models.user import User
from app.models.candidate_insights import CandidateInsights
import json
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run_audit():
    db = SessionLocal()
    
    # Get top 10 jobs by final_score
    jobs = db.query(JobSearchResult).filter(JobSearchResult.final_score.isnot(None)).order_by(JobSearchResult.final_score.desc()).limit(10).all()
    
    for i, job in enumerate(jobs, 1):
        print(f"\n[{i}] {job.job_title} @ {job.company_name}")
        print(f"Hybrid Score: {job.final_score:.2f}")
        print(f"Semantic Score: {job.semantic_score:.2f}")
        print(f"Deterministic Score: {job.deterministic_score:.2f}")
        print(f"Matching Skills: {job.matching_skills}")
        print(f"Missing Skills: {job.missing_skills}")
        
    print("\n--- MATCHING CONFIG ---")
    print(f"DOMAIN_WEIGHT: {matching_config.DOMAIN_WEIGHT}")
    print(f"TECH_WEIGHT: {matching_config.TECH_WEIGHT}")
    print(f"CAPABILITY_WEIGHT: {matching_config.CAPABILITY_WEIGHT}")
    print(f"LEVEL_WEIGHT: {matching_config.LEVEL_WEIGHT}")
    
    db.close()

if __name__ == "__main__":
    run_test = run_audit()
