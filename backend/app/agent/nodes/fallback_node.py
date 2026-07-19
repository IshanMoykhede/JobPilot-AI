import logging
from app.agent.schemas.agent_state import AgentState

logger = logging.getLogger(__name__)

async def fallback_node(state: AgentState) -> dict:
    """
    Fallback agent handling unknown intents or exceptions during graph execution.
    """
    intent = state.get("intent", "UNKNOWN")
    logger.warning(f"[FallbackNode] Handling request with intent: {intent}")
    
    return {
        "response": {
            "status": "FALLBACK",
            "message": "I'm sorry, I couldn't process your request or I don't support that feature yet. Could you try asking about jobs, resume tailoring, or interview preparation?"
        }
    }
