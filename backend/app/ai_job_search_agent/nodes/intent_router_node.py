from langchain_core.messages import SystemMessage, HumanMessage
from app.ai_job_search_agent.state import V2AgentState
from app.ai_job_search_agent.schemas import IntentClassification, ActivityLog
from app.gateway.llm_gateway import LLMGateway

INTENT_ROUTER_PROMPT = """You are the core routing engine for a Job Search AI Assistant.
Your ONLY job is to identify the user's intent based on their query.

Choose EXACTLY ONE of the following intents:
- NEW_SEARCH: The user is providing a completely new job search query.
- FOLLOW_UP: The user is applying a filter, asking a question, or modifying an EXISTING search.
- GENERAL: The user is saying hello, asking a generic career question, or something completely unrelated to finding a job right now.
"""

async def intent_router_node(state: V2AgentState) -> dict:
    """
    Identifies the workflow to activate based on the user's query.
    Takes user_query from the state and updates the intent and activity_logs.
    """
    user_query = state.get("user_query", "")
    
    if not user_query.strip():
        # Fallback if no query is provided
        return {
            "intent": "GENERAL",
            "activity_logs": [
                ActivityLog(
                    node_name="intent_router_node",
                    input_summary="Empty query",
                    reasoning="No user query was provided in the state.",
                    output_summary="Classified as GENERAL"
                )
            ]
        }
        
    llm = LLMGateway.get_llm(temperature=0.0)
    structured_llm = llm.with_structured_output(IntentClassification)
    
    messages = [
        SystemMessage(content=INTENT_ROUTER_PROMPT),
        HumanMessage(content=user_query)
    ]
    
    response = await structured_llm.ainvoke(messages)
    
    log = ActivityLog(
        node_name="intent_router_node",
        input_summary=f"User query: '{user_query}'",
        reasoning="Analyzed the user query using the LLM to determine the core intent.",
        output_summary=f"Classified intent as {response.intent.value}"
    )
    
    return {
        "intent": response.intent.value,
        "activity_logs": [log]
    }
