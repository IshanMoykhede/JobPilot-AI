from app.agent.schemas.agent_state import AgentState

async def resume_tailoring_node(state: AgentState) -> dict:
    return {
        "response": {
            "status": "NOT_IMPLEMENTED",
            "message": "Resume Tailoring agent is not implemented yet."
        }
    }
