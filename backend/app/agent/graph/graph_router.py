import logging
from app.agent.schemas.agent_state import AgentState
from app.agent.core.agent_enums import Intent

logger = logging.getLogger(__name__)

def route_intent(state: AgentState) -> str:
    """
    Conditional routing logic for the LangGraph orchestrator.
    Maps the intent stored in state to the corresponding node name.
    """
    intent = state.get("intent")
    
    if intent == Intent.JOB_SEARCH.value:
        return "job_search"
    elif intent == Intent.GENERAL_CHAT.value:
        return "general_chat"
    elif intent == Intent.FOLLOW_UP.value:
        return "follow_up"
    elif intent == Intent.RESUME_TAILORING.value:
        return "resume_tailoring"
    elif intent == Intent.INTERVIEW_PREPARATION.value:
        return "interview_preparation"
    else:
        logger.warning(f"[GraphRouter] Unknown or missing intent '{intent}', routing to fallback.")
        return "fallback"
