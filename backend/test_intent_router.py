import os
import sys
import json

# Add backend to path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.resume_tailoring_agent_v2.state import ResumeTailoringState
from app.resume_tailoring_agent_v2.nodes.intent_router_node import determine_intent

def run_tests():
    output = []
    output.append("=== INTENT ROUTER TESTS ===\n")
    
    # ---------------------------------------------------------
    # Test 1: Start a new section
    # ---------------------------------------------------------
    state1 = ResumeTailoringState(
        session_id="test1",
        pending_sections=["projects", "skills"],
        current_section=None,
        messages=[
            {"role": "user", "content": "Let's start working on the projects section."}
        ]
    )
    res1 = determine_intent(state1)
    output.append(f"Test 1 (Start Section): 'Let's start working on the projects section.'")
    output.append(f"Result: {res1.model_dump_json(indent=2)}\n")
    
    # ---------------------------------------------------------
    # Test 2: Revise the current section
    # ---------------------------------------------------------
    state2 = ResumeTailoringState(
        session_id="test2",
        pending_sections=["skills"],
        current_section="projects",
        messages=[
            {"role": "assistant", "content": "I generated your projects draft."},
            {"role": "user", "content": "Can you make the AI job matcher bullet points a bit shorter?"}
        ]
    )
    res2 = determine_intent(state2)
    output.append(f"Test 2 (Revise Section): 'Can you make the AI job matcher bullet points a bit shorter?'")
    output.append(f"Result: {res2.model_dump_json(indent=2)}\n")

    # ---------------------------------------------------------
    # Test 3: Approve and Next
    # ---------------------------------------------------------
    state3 = ResumeTailoringState(
        session_id="test3",
        pending_sections=["skills"],
        current_section="projects",
        messages=[
            {"role": "assistant", "content": "Here is the revised projects section."},
            {"role": "user", "content": "This looks perfect. Let's move on."}
        ]
    )
    res3 = determine_intent(state3)
    output.append(f"Test 3 (Approve and Next): 'This looks perfect. Let's move on.'")
    output.append(f"Result: {res3.model_dump_json(indent=2)}\n")
    
    # ---------------------------------------------------------
    # Test 4: Finish
    # ---------------------------------------------------------
    state4 = ResumeTailoringState(
        session_id="test4",
        pending_sections=["skills"],
        current_section="projects",
        messages=[
            {"role": "assistant", "content": "What would you like to do?"},
            {"role": "user", "content": "Actually I have to go, let's stop here for today."}
        ]
    )
    res4 = determine_intent(state4)
    output.append(f"Test 4 (Finish): 'Actually I have to go, let's stop here for today.'")
    output.append(f"Result: {res4.model_dump_json(indent=2)}\n")
    
    # Write output to file
    with open("router_test_results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
        
    print("Tests completed. Results saved to router_test_results.txt")

if __name__ == "__main__":
    run_tests()
