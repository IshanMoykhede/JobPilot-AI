from app.agent.schemas.agent_state import AgentState

async def general_chat_node(state: AgentState) -> dict:
    return {
        "response": {
            "status": "NOT_IMPLEMENTED",
            "message": "General Chat agent is not implemented yet."
        }
    }
