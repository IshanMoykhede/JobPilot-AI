from app.agent.schemas.agent_state import AgentState

async def interview_node(state: AgentState) -> dict:
    return {
        "response": {
            "status": "NOT_IMPLEMENTED",
            "message": "Interview Preparation agent is not implemented yet."
        }
    }
