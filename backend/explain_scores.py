import os
import random
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.job_search.models.job_knowledge import JobKnowledge
from app.models.candidate_profile import CandidateProfile
from app.matching.services.deterministic_matcher import DeterministicMatcher

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run():
    db = SessionLocal()
    
    profile = db.query(CandidateProfile).first()
    candidate_knowledge = profile.parsed_json
    
    all_jks = db.query(JobKnowledge).all()
    sample = random.sample(all_jks, min(5, len(all_jks)))
    
    print("CANDIDATE INFO:")
    print("Domains:", candidate_knowledge.get("candidate_identity", {}).get("engineering_domains", []))
    print("Techs:", candidate_knowledge.get("candidate_identity", {}).get("primary_technology_stack", []))
    print("Caps:", candidate_knowledge.get("candidate_identity", {}).get("strongest_capabilities", []))
    print("Level:", candidate_knowledge.get("candidate_level", "Mid"))
    print("-" * 40)
    
    for idx, jk in enumerate(sample):
        print(f"\n[{idx+1}] {jk.job_title}")
        dom_score = DeterministicMatcher.compare_domains(candidate_knowledge, jk)
        tech_score, _, _ = DeterministicMatcher.compare_technologies(candidate_knowledge, jk)
        cap_score, _, _ = DeterministicMatcher.compare_capabilities(candidate_knowledge, jk)
        lvl_score = DeterministicMatcher.compare_levels(candidate_knowledge, jk)
        
        print(f"Domain score: {dom_score}")
        print(f"Technology score: {tech_score}")
        print(f"Capability score: {cap_score}")
        print(f"Level score: {lvl_score}")
        print(f"Final deterministic score: {dom_score + tech_score + cap_score + lvl_score}")
        
    db.close()

if __name__ == "__main__":
    run()
