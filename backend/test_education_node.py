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
from app.resume_tailoring_agent_v2.nodes.education_section_node import education_section_node

def extract_and_test():
    db = SessionLocal()
    try:
        job_doc = db.query(JobKnowledge).first()
        cand_doc = db.query(CandidateInsights).first()
        
        job_knowledge = job_doc.raw_knowledge
        user_knowledge = cand_doc.artifact_json
            
        print("Starting Education Node testing...\n")
        
        output = []
        output.append("=== EDUCATION NODE TESTS ===\n")
        
        state1 = ResumeTailoringState(
            session_id="test_edu_1",
            job_knowledge=job_knowledge,
            user_knowledge=user_knowledge,
            messages=[{"role": "user", "content": "Let's work on my education."}],
            drafts={}
        )
        
        try:
            res1 = education_section_node(state1)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"Rate limit hit! Waiting 60 seconds... ({e})")
                time.sleep(60)
                res1 = education_section_node(state1)
            else:
                raise e
                
        output.append("Test 1 (Initial Generation):")
        output.append(f"Draft Array (state.drafts): {json.dumps(res1.drafts.get('education', []), indent=2)}")
        output.append(f"Assistant Message: {res1.messages[-1].get('content') if res1.messages else 'No message'}\n")
        
        # ---------------------------------------------
        # Test 2: Revision (Add GPA)
        # ---------------------------------------------
        print("Waiting a few seconds before Test 2...")
        time.sleep(10)
        
        print("Running Test 2 (Revision Request)...")
        state2 = ResumeTailoringState(
            session_id="test_edu_2",
            job_knowledge=job_knowledge,
            user_knowledge=user_knowledge,
            drafts=res1.drafts,
            messages=res1.messages + [{"role": "user", "content": "add 7.60 cgpa to my B.E., 72 percent in hsc and 87 percent in ssc"}]
        )
        
        try:
            res2 = education_section_node(state2)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"Rate limit hit! Waiting 60 seconds... ({e})")
                time.sleep(60)
                res2 = education_section_node(state2)
            else:
                raise e
                
        output.append("Test 2 (Revision Request): 'add 7.60 cgpa to my B.E., 72 percent in hsc and 87 percent in ssc'")
        output.append(f"Draft Array (state.drafts): {json.dumps(res2.drafts.get('education', []), indent=2)}")
        output.append(f"Assistant Message: {res2.messages[-1].get('content') if res2.messages else 'No message'}\n")
        
        with open("education_test_results.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
            
        print("Education node tests completed. Results saved to education_test_results.txt")
        
    finally:
        db.close()

if __name__ == "__main__":
    extract_and_test()
