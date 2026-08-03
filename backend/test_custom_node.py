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
from app.resume_tailoring_agent_v2.nodes.custom_section_node import custom_section_node

def extract_and_test():
    db = SessionLocal()
    try:
        job_doc = db.query(JobKnowledge).first()
        cand_doc = db.query(CandidateInsights).first()
        
        job_knowledge = job_doc.raw_knowledge
        user_knowledge = cand_doc.artifact_json
            
        print("Starting Custom Section Node testing...\n")
        
        output = []
        output.append("=== CUSTOM SECTION NODE TESTS ===\n")
        
        # ---------------------------------------------
        # Test 1: Achievements
        # ---------------------------------------------
        print("Running Test 1 (Achievements)...")
        state1 = ResumeTailoringState(
            session_id="test_custom_1",
            job_knowledge=job_knowledge,
            user_knowledge=user_knowledge,
            messages=[{"role": "user", "content": "Add my 1st place win at the Smart India Hackathon to an Achievements section. We built an AI agent."}],
            drafts={}
        )
        
        try:
            res1 = custom_section_node(state1)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"Rate limit hit! Waiting 60 seconds... ({e})")
                time.sleep(60)
                res1 = custom_section_node(state1)
            else:
                raise e
                
        output.append("Test 1 Request: 'Add my 1st place win at the Smart India Hackathon to an Achievements section. We built an AI agent.'")
        output.append(f"Draft Array (state.drafts['custom']): {json.dumps(res1.drafts.get('custom', []), indent=2)}")
        output.append(f"Assistant Message: {res1.messages[-1].get('content') if res1.messages else 'No message'}\n")
        
        # ---------------------------------------------
        # Test 2: Research (Appending to state)
        # ---------------------------------------------
        print("Waiting 65 seconds for Rate Limit before Test 2...")
        time.sleep(65)
        
        print("Running Test 2 (Research)...")
        state2 = ResumeTailoringState(
            session_id="test_custom_2",
            job_knowledge=job_knowledge,
            user_knowledge=user_knowledge,
            drafts=res1.drafts,
            messages=res1.messages + [{"role": "user", "content": "Now add a Research section. I published an IEEE paper on RAG pipelines."}]
        )
        
        try:
            res2 = custom_section_node(state2)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"Rate limit hit! Waiting 60 seconds... ({e})")
                time.sleep(60)
                res2 = custom_section_node(state2)
            else:
                raise e
                
        output.append("Test 2 Request: 'Now add a Research section. I published an IEEE paper on RAG pipelines.'")
        output.append(f"Draft Array (state.drafts['custom']): {json.dumps(res2.drafts.get('custom', []), indent=2)}")
        output.append(f"Assistant Message: {res2.messages[-1].get('content') if res2.messages else 'No message'}\n")

        # ---------------------------------------------
        # Test 3: Co-Curricular
        # ---------------------------------------------
        print("Waiting 65 seconds for Rate Limit before Test 3...")
        time.sleep(65)
        
        print("Running Test 3 (Co-Curricular)...")
        state3 = ResumeTailoringState(
            session_id="test_custom_3",
            job_knowledge=job_knowledge,
            user_knowledge=user_knowledge,
            drafts=res2.drafts,
            messages=res2.messages + [{"role": "user", "content": "Finally add a Co-curricular activities section showing I was the GDSC Lead for my campus."}]
        )
        
        try:
            res3 = custom_section_node(state3)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"Rate limit hit! Waiting 60 seconds... ({e})")
                time.sleep(60)
                res3 = custom_section_node(state3)
            else:
                raise e
                
        output.append("Test 3 Request: 'Finally add a Co-curricular activities section showing I was the GDSC Lead for my campus.'")
        output.append(f"Draft Array (state.drafts['custom']): {json.dumps(res3.drafts.get('custom', []), indent=2)}")
        output.append(f"Assistant Message: {res3.messages[-1].get('content') if res3.messages else 'No message'}\n")
        
        with open("custom_test_results.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
            
        print("Custom node tests completed. Results saved to custom_test_results.txt")
        
    finally:
        db.close()

if __name__ == "__main__":
    extract_and_test()
