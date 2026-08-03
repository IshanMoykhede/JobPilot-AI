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
from app.resume_tailoring_agent_v2.nodes.experience_section_node import experience_section_node

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
        
        # Inject mock experience so the LLM actually has data to generate a draft from!
        user_knowledge["experience_intelligence"] = [
            {
                "title": "Software Engineering Intern",
                "company": "Tech Innovations Inc.",
                "dates": "May 2023 - August 2023",
                "description": "Worked on migrating the backend to a microservices architecture using Python and FastAPI. Implemented a data analytics pipeline for processing user logs. Collaborated closely with the AI team.",
                "technologies_used": ["Python", "FastAPI", "PostgreSQL", "Docker"]
            }
        ]
            
        print("Starting Experience Node testing with Rate Limit handling...\n")
        
        output = []
        output.append("=== EXPERIENCE NODE TESTS ===\n")
        
        # ---------------------------------------------
        # Test 1: Initial Generation
        # ---------------------------------------------
        print("Running Test 1 (Initial Generation)...")
        state1 = ResumeTailoringState(
            session_id="test_exp_1",
            job_knowledge=job_knowledge,
            user_knowledge=user_knowledge,
            messages=[{"role": "user", "content": "Let's work on my experience."}],
            drafts={}
        )
        
        try:
            res1 = experience_section_node(state1)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"Rate limit hit! Waiting 60 seconds... ({e})")
                time.sleep(60)
                res1 = experience_section_node(state1)
            else:
                raise e
                
        output.append("Test 1 (Initial Generation):")
        output.append(f"Draft Array (state.drafts): {json.dumps(res1.drafts.get('experience', []), indent=2)}")
        output.append(f"Assistant Message: {res1.messages[-1].get('content') if res1.messages else 'No message'}\n")
        
        # ---------------------------------------------
        # Test 2: Revision (User feedback)
        # ---------------------------------------------
        print("Waiting a few seconds before Test 2...")
        time.sleep(10)
        
        print("Running Test 2 (Revision)...")
        state2 = ResumeTailoringState(
            session_id="test_exp_2",
            job_knowledge=job_knowledge,
            user_knowledge=user_knowledge,
            drafts=res1.drafts,
            messages=res1.messages + [{"role": "user", "content": "Can you emphasize the soft skills I gained during the internship instead of just technical tools?"}]
        )
        
        try:
            res2 = experience_section_node(state2)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"Rate limit hit! Waiting 60 seconds... ({e})")
                time.sleep(60)
                res2 = experience_section_node(state2)
            else:
                raise e
                
        output.append("Test 2 (Revision Request): 'Can you emphasize the soft skills I gained during the internship instead of just technical tools?'")
        output.append(f"Draft Array (state.drafts): {json.dumps(res2.drafts.get('experience', []), indent=2)}")
        output.append(f"Assistant Message: {res2.messages[-1].get('content') if res2.messages else 'No message'}\n")

        # ---------------------------------------------
        # Test 3: Edge Case (Completely unrelated request)
        # ---------------------------------------------
        print("Waiting a few seconds before Test 3...")
        time.sleep(10)
        
        print("Running Test 3 (Edge Case)...")
        state3 = ResumeTailoringState(
            session_id="test_exp_3",
            job_knowledge=job_knowledge,
            user_knowledge=user_knowledge,
            drafts=res2.drafts,
            messages=res2.messages + [{"role": "user", "content": "I have no actual work experience except working at a coffee shop, what should I put?"}]
        )
        
        try:
            res3 = experience_section_node(state3)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"Rate limit hit! Waiting 60 seconds... ({e})")
                time.sleep(60)
                res3 = experience_section_node(state3)
            else:
                raise e
                
        output.append("Test 3 (Edge Case): 'I have no actual work experience except working at a coffee shop, what should I put?'")
        output.append(f"Draft Array (state.drafts): {json.dumps(res3.drafts.get('experience', []), indent=2)}")
        output.append(f"Assistant Message: {res3.messages[-1].get('content') if res3.messages else 'No message'}\n")

        # Write output to file
        with open("experience_test_results.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
            
        print("Experience node tests completed. Results saved to experience_test_results.txt")
        
    finally:
        db.close()

if __name__ == "__main__":
    extract_and_test()
