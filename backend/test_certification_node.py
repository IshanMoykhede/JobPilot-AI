import os
import sys
import json
import time

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.job_search_agent.models.job_knowledge import JobKnowledge
from app.models.candidate_insights import CandidateInsights
from app.models.candidate_profile import CandidateProfile
from app.models.user import User
from app.resume_tailoring_agent_v2.state import ResumeTailoringState
from app.resume_tailoring_agent_v2.nodes.certification_section_node import certification_section_node

def extract_and_test():
    db = SessionLocal()
    try:
        # Extract Job Knowledge
        job_doc = db.query(JobKnowledge).first()
        if not job_doc:
            print("No JobKnowledge found in DB.")
            return
        
        job_knowledge = job_doc.raw_knowledge
            
        # Extract Candidate Insights
        cand_doc = db.query(CandidateInsights).first()
        if not cand_doc:
            print("No CandidateInsights found in DB.")
            return
            
        user_knowledge = cand_doc.artifact_json
            
        print("Starting Certification Node testing with Rate Limit handling...\n")
        
        output = []
        output.append("=== CERTIFICATION NODE TESTS ===\n")
        
        # ---------------------------------------------
        # Test 1: Initial Generation
        # ---------------------------------------------
        print("Running Test 1 (Initial Generation)...")
        state1 = ResumeTailoringState(
            session_id="test_cert_1",
            job_knowledge=job_knowledge,
            user_knowledge=user_knowledge,
            messages=[{"role": "user", "content": "Let's work on my certifications."}],
            drafts={}
        )
        
        try:
            res1 = certification_section_node(state1)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"Rate limit hit! Waiting 60 seconds... ({e})")
                time.sleep(60)
                res1 = certification_section_node(state1)
            else:
                raise e
                
        output.append("Test 1 (Initial Generation):")
        output.append(f"Draft Array (state.drafts): {json.dumps(res1.drafts.get('certifications', []), indent=2)}")
        output.append(f"Assistant Message: {res1.messages[-1].get('content') if res1.messages else 'No message'}\n")
        
        # Write output to file
        with open("certification_test_results.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
            
        print("Certification node tests completed. Results saved to certification_test_results.txt")
        
    finally:
        db.close()

if __name__ == "__main__":
    extract_and_test()
