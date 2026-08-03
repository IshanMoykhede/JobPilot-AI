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

from app.resume_tailoring_agent_v2.graph import resume_tailoring_app

def test_orchestrator():
    db = SessionLocal()
    try:
        job_doc = db.query(JobKnowledge).first()
        cand_doc = db.query(CandidateInsights).first()
        
        job_knowledge = job_doc.raw_knowledge
        user_knowledge = cand_doc.artifact_json
            
        print("Starting LangGraph Orchestrator testing...\n")
        
        output = []
        output.append("=== LANGGRAPH ORCHESTRATOR TESTS ===\n")
        
        # Test 1: Let's work on my projects
        # We need a configurable thread_id for the MemorySaver checkpointer
        config = {"configurable": {"thread_id": "test_thread_1"}}
        
        print("Running Test 1 (Routing to Projects)...")
        state_input = {
            "session_id": "test_thread_1",
            "job_knowledge": job_knowledge,
            "user_knowledge": user_knowledge,
            "messages": [{"role": "user", "content": "Let's work on my projects section."}],
            "drafts": {},
            "active_section": "general"
        }
        
        try:
            # We use stream() to observe the node transitions
            for event in resume_tailoring_app.stream(state_input, config):
                for node_name, state in event.items():
                    print(f"--> Traversed Node: {node_name}")
                    output.append(f"Node Executed: {node_name}")
                    
                    if node_name != "intent_router":
                        output.append(f"State active_section: {state.get('active_section')}")
                        output.append(f"Assistant Message: {state.get('messages', [])[-1].get('content')}")
                        output.append(f"Drafts Keys: {list(state.get('drafts', {}).keys())}\n")
                        
        except Exception as e:
            output.append(f"Error during graph execution: {e}")
            raise e
            
        with open("graph_test_results.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
            
        print("Graph tests completed. Results saved to graph_test_results.txt")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_orchestrator()
