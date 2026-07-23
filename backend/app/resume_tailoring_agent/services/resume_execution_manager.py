import json
import logging
from typing import Generator
from app.resume_tailoring_agent.graph import get_resume_agent_app
from app.resume_tailoring_agent.state import ResumeAgentState
from app.resume_tailoring_agent.schemas.messaging import ResumeMessage, MessageRole, MessageType, MessageSource
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ResumeExecutionManager:
    """
    Manages LangGraph execution lifecycle and streaming.
    Does not interact with database ORM models.
    """
    
    @staticmethod
    def _serialize_state(state: ResumeAgentState | dict) -> str:
        """Helper to cleanly serialize the state for the frontend."""
        if isinstance(state, dict):
            try:
                state = ResumeAgentState(**state)
            except Exception as e:
                logger.error(f"Failed to parse state dict: {e}")
                # Fallback to simple dict access if parsing fails
                state_dict = {
                    "resume_id": state.get("resume_id"),
                    "current_section": state.get("current_section"),
                    "pending_sections": state.get("pending_sections", []),
                    "response_message": state.get("response_message"),
                    "resume_content": state.get("resume_content"),
                    "messages": state.get("messages", [])
                }
                return json.dumps(state_dict)

        state_dict = {
            "resume_id": state.resume_id,
            "current_section": state.current_section.value if state.current_section else None,
            "pending_sections": [s.value for s in state.pending_sections] if state.pending_sections else [],
            "response_message": state.response_message
        }
        if hasattr(state, "resume_content") and state.resume_content:
            state_dict["resume_content"] = state.resume_content.model_dump()
        else:
            state_dict["resume_content"] = None
            
        if hasattr(state, "messages") and state.messages:
            state_dict["messages"] = [msg.model_dump() for msg in state.messages]
        else:
            state_dict["messages"] = []
            
        return json.dumps(state_dict)

    def stream_graph_execution(self, initial_state: ResumeAgentState, thread_id: str) -> Generator[str, None, None]:
        """
        Invokes LangGraph with the initial state and streams SSE updates.
        """
        app = get_resume_agent_app()
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Yield initial state
            yield f"data: {self._serialize_state(initial_state)}\n\n"
            
            for state_val in app.stream(initial_state, config=config, stream_mode="values"):
                # Yield the updated state
                yield f"data: {self._serialize_state(state_val)}\n\n"
                
            yield "event: close\ndata: {}\n\n"
        except Exception as e:
            logger.error(f"Error during graph execution: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'detail': str(e)})}\n\n"

    def continue_graph_execution(self, thread_id: str, user_message: str) -> Generator[str, None, None]:
        """
        Resumes LangGraph execution from a checkpoint using thread_id.
        """
        app = get_resume_agent_app()
        config = {"configurable": {"thread_id": thread_id}}
        
        # Load current state from checkpointer
        current_state_dict = app.get_state(config)
        if not current_state_dict or not current_state_dict.values:
            yield f"event: error\ndata: {json.dumps({'detail': 'No active session found for this resume.'})}\n\n"
            return
            
        # Append the new message to the state
        state_values = current_state_dict.values
        
        new_msg = ResumeMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            role=MessageRole.USER,
            message_type=MessageType.HUMAN_INPUT_RESPONSE,
            from_node=MessageSource.USER,
            to_node=MessageSource.INTENT_ROUTER,
            content=user_message
        )
        
        current_messages = state_values.get("messages", [])
        updated_messages = current_messages + [new_msg]
        
        # We can update the state explicitly via update_state, then stream with no input
        app.update_state(config, {"messages": updated_messages})

        try:
            for state_val in app.stream(None, config=config, stream_mode="values"):
                yield f"data: {self._serialize_state(state_val)}\n\n"
                
            yield "event: close\ndata: {}\n\n"
        except Exception as e:
            logger.error(f"Error during graph execution: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'detail': str(e)})}\n\n"

    def retry_graph_execution(self, thread_id: str) -> Generator[str, None, None]:
        """
        Retries LangGraph execution from the last checkpoint without adding new messages.
        """
        app = get_resume_agent_app()
        config = {"configurable": {"thread_id": thread_id}}
        
        # Load current state from checkpointer
        current_state_dict = app.get_state(config)
        if not current_state_dict or not current_state_dict.values:
            yield f"event: error\ndata: {json.dumps({'detail': 'No active session found for this resume.'})}\n\n"
            return
            
        try:
            for state_val in app.stream(None, config=config, stream_mode="values"):
                yield f"data: {self._serialize_state(state_val)}\n\n"
                
            yield "event: close\ndata: {}\n\n"
        except Exception as e:
            logger.error(f"Error during graph execution retry: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'detail': str(e)})}\n\n"

    def get_graph_state(self, thread_id: str) -> dict:
        """
        Retrieves the raw current state of the graph execution from the checkpointer.
        """
        app = get_resume_agent_app()
        config = {"configurable": {"thread_id": thread_id}}
        state_snapshot = app.get_state(config)
        if state_snapshot and hasattr(state_snapshot, "values"):
            return state_snapshot.values
        return None
