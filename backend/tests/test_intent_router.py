import asyncio
from app.resume_tailoring_agent.nodes.intent_router_node import intent_router_node, TargetNode
from app.resume_tailoring_agent.state import ResumeAgentState

def create_mock_state(user_query: str, history: list = None) -> ResumeAgentState:
    return ResumeAgentState(
        resume_id="test_id",
        session_id="test_session",
        user_id="test_user",
        messages=history or [],
        user_query=user_query,
        pending_sections=[]
    )

def test_intent_router():
    print("=== Testing Intent Router LLM Classification ===\n")
    
    test_cases = [
        {
            "name": "Modify specific section (Projects)",
            "query": "Can you add a project about my new React application?",
            "history": [],
            "expected_node": TargetNode.PROJECT_GENERATOR.value
        },
        {
            "name": "Modify specific section (Experience)",
            "query": "Update my work experience to include my time at Google.",
            "history": [],
            "expected_node": TargetNode.EXPERIENCE_GENERATOR.value
        },
        {
            "name": "Human-in-the-loop response (Skills)",
            "query": "I know Python, JavaScript, and Docker.",
            "history": [
                {"role": "assistant", "content": "I couldn't find enough information about your skills. What programming languages and tools do you know?"}
            ],
            "expected_node": TargetNode.SKILLS_GENERATOR.value
        },
        {
            "name": "Download PDF",
            "query": "I am happy with it, please give me the pdf now.",
            "history": [],
            "expected_node": TargetNode.PDF_GENERATOR.value
        },
        {
            "name": "General question / Explanation",
            "query": "How exactly does this resume AI work?",
            "history": [],
            "expected_node": TargetNode.EXPLANATION_NODE.value
        },
        {
            "name": "Greeting / Conversation",
            "query": "Hello there!",
            "history": [],
            "expected_node": TargetNode.EXPLANATION_NODE.value
        }
    ]

    passed = 0
    for i, tc in enumerate(test_cases, 1):
        print(f"Test {i}: {tc['name']}")
        print(f"Query: '{tc['query']}'")
        
        state = create_mock_state(user_query=tc['query'], history=tc['history'])
        
        try:
            # Run the node logic
            updated_state = intent_router_node(state)
            actual_node = updated_state.next_node
            
            if actual_node == tc['expected_node']:
                print(f"Result: PASS (Mapped to {actual_node})")
                passed += 1
            else:
                print(f"Result: FAIL (Expected {tc['expected_node']}, got {actual_node})")
        except Exception as e:
            print(f"Result: ERROR ({str(e)})")
            
        print("-" * 50)
        
    print(f"\nSummary: {passed}/{len(test_cases)} tests passed.")

if __name__ == "__main__":
    # Ensure dotenv is loaded so LangChain API keys work
    from dotenv import load_dotenv
    load_dotenv()
    test_intent_router()
