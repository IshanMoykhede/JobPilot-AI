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
from app.resume_tailoring_agent_v2.nodes.project_section_node import project_section_node

def extract_and_test():
    db = SessionLocal()
    try:
        # Extract Job Knowledge
        job_doc = db.query(JobKnowledge).first()
        if not job_doc:
            print("No JobKnowledge found in DB.")
            return
        
        job_knowledge = job_doc.raw_knowledge
        with open("test_job_knowledge.json", "w", encoding="utf-8") as f:
            json.dump(job_knowledge, f, indent=2)
            
        # Extract Candidate Insights
        cand_doc = db.query(CandidateInsights).first()
        if not cand_doc:
            print("No CandidateInsights found in DB.")
            return
            
        user_knowledge = cand_doc.artifact_json
        with open("test_candidate_insights.json", "w", encoding="utf-8") as f:
            json.dump(user_knowledge, f, indent=2)
            
        print("Data extracted successfully to JSON files.")
        print("Starting Project Node testing with Rate Limit handling...\n")
        
        output = []
        output.append("=== PROJECT NODE TESTS ===\n")
        
        # ---------------------------------------------
        # Test 1: Initial Generation
        # ---------------------------------------------
        print("Running Test 1 (Initial Generation)...")
        state1 = ResumeTailoringState(
            session_id="test_projects_1",
            job_knowledge=job_knowledge,
            user_knowledge=user_knowledge,
            messages=[{"role": "user", "content": "Let's start the projects section."}],
            drafts={}
        )
        
        try:
            res1 = project_section_node(state1)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"Rate limit hit! Waiting 60 seconds... ({e})")
                time.sleep(60)
                try:
                    res1 = project_section_node(state1)
                except Exception as retry_e:
                    print("Rate limit hit again. Stopping flow to prevent infinite loop.")
                    return
            else:
                raise e
                
        output.append("Test 1 (Initial Generation):")
        output.append(f"Draft Array (state.drafts): {json.dumps(res1.drafts.get('projects', []), indent=2)}")
        output.append(f"Assistant Message: {res1.messages[-1].get('content') if res1.messages else 'No message'}\n")
        
        # ---------------------------------------------
        # Test 2: Revision (Human in the loop)
        # ---------------------------------------------
        print("Waiting a few seconds before Test 2 to avoid instant rate limit...")
        time.sleep(10)
        
        print("Running Test 2 (Revision)...")
        # Copy the drafts array from res1 to simulate conversation continuity
        state2 = ResumeTailoringState(
            session_id="test_projects_2",
            job_knowledge=job_knowledge,
            user_knowledge=user_knowledge,
            drafts=res1.drafts,
            messages=res1.messages + [{"role": "user", "content": "Can you make the bullet points shorter and focus strictly on the tech stack?"}]
        )
        
        try:
            res2 = project_section_node(state2)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"Rate limit hit! Waiting 60 seconds... ({e})")
                time.sleep(60)
                try:
                    res2 = project_section_node(state2)
                except Exception as retry_e:
                    print("Rate limit hit again. Stopping flow.")
                    return
            else:
                raise e
                
        output.append("Test 2 (Revision Request): 'Can you make the bullet points shorter and focus strictly on the tech stack?'")
        output.append(f"Draft Array (state.drafts): {json.dumps(res2.drafts.get('projects', []), indent=2)}")
        output.append(f"Assistant Message: {res2.messages[-1].get('content') if res2.messages else 'No message'}\n")

        # ---------------------------------------------
        # Test 3: Force inclusion of a dropped project
        # ---------------------------------------------
        print("Waiting a few seconds before Test 3...")
        time.sleep(10)
        
        print("Running Test 3 (Adding CampusConnect)...")
        state3 = ResumeTailoringState(
            session_id="test_projects_3",
            job_knowledge=job_knowledge,
            user_knowledge=user_knowledge,
            drafts=res2.drafts,
            messages=res2.messages + [{"role": "user", "content": "I noticed you didn't include the CampusConnect full-stack project. Please add it to the bottom of the projects section."}]
        )
        
        try:
            res3 = project_section_node(state3)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"Rate limit hit! Waiting 60 seconds... ({e})")
                time.sleep(60)
                try:
                    res3 = project_section_node(state3)
                except Exception as retry_e:
                    print("Rate limit hit again. Stopping flow.")
                    return
            else:
                raise e
                
        output.append("Test 3 (Add Missing Project): 'I noticed you didn't include the CampusConnect full-stack project. Please add it...'")
        output.append(f"Draft Array (state.drafts): {json.dumps(res3.drafts.get('projects', []), indent=2)}")
        output.append(f"Assistant Message: {res3.messages[-1].get('content') if res3.messages else 'No message'}\n")

        # Write output to file
        with open("project_test_results.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
            
        print("Project node tests completed. Results saved to project_test_results.txt")
        
    finally:
        db.close()

if __name__ == "__main__":
    extract_and_test()
