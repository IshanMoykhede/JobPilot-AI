import uuid
import json
import logging
import threading
from datetime import datetime, timezone
from typing import Generator, Dict, Any, Optional

from app.resume_tailoring_agent.graph import get_resume_agent_app
from app.resume_tailoring_agent.state import ResumeAgentState
from app.resume_tailoring_agent.schemas.messaging import ResumeMessage, MessageRole, MessageType, MessageSource
from app.resume_tailoring_agent.schemas.common import ResumeSectionType, ResumeContent

logger = logging.getLogger(__name__)

# Thread-safe cancellation tracker
_cancel_flags: Dict[str, bool] = {}
_cancel_lock = threading.Lock()

def request_cancel_execution(thread_id: str):
    """Signals that the current execution for thread_id should be cancelled."""
    with _cancel_lock:
        _cancel_flags[thread_id] = True
    logger.info(f"[Concurrency] Requested cancellation for thread {thread_id}")

def clear_cancel_flag(thread_id: str):
    """Clears the cancellation flag for thread_id."""
    with _cancel_lock:
        _cancel_flags[thread_id] = False

def is_execution_cancelled(thread_id: str) -> bool:
    """Returns True if the cancellation flag for thread_id is set."""
    with _cancel_lock:
        return _cancel_flags.get(thread_id, False)


class ResumeExecutionManager:
    """
    Manages LangGraph instantiation, execution, state checkpoints, and concurrency controls.
    """
    
    def _serialize_state(self, state: Any) -> str:
        """Serializes the state object/dict to a clean JSON string."""
        if not state:
            return "{}"
            
        if isinstance(state, dict):
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
            "current_section": state.current_section if state.current_section else None,
            "pending_sections": state.pending_sections if state.pending_sections else [],
            "response_message": state.response_message
        }
        if hasattr(state, "resume_content") and state.resume_content:
            state_dict["resume_content"] = state.resume_content if isinstance(state.resume_content, dict) else state.resume_content.model_dump(mode="json")
        else:
            state_dict["resume_content"] = None
            
        if hasattr(state, "messages") and state.messages:
            state_dict["messages"] = [msg if isinstance(msg, dict) else msg.model_dump(mode="json") for msg in state.messages]
        else:
            state_dict["messages"] = []
            
        return json.dumps(state_dict)

    def stream_graph_execution(self, initial_state: ResumeAgentState, thread_id: str) -> Generator[str, None, None]:
        """
        Invokes LangGraph with the initial state and streams SSE updates with sequence IDs.
        Supports cancellation checkpoints between graph steps.
        """
        app = get_resume_agent_app()
        config = {"configurable": {"thread_id": thread_id}}
        clear_cancel_flag(thread_id)
        
        try:
            # Yield initial state (Sequence ID 1)
            seq_id = 1
            payload = {
                "seq_id": seq_id,
                "state": json.loads(self._serialize_state(initial_state))
            }
            yield f"data: {json.dumps(payload)}\n\n"
            
            for state_val in app.stream(initial_state, config=config, stream_mode="values"):
                # Concurrency check
                if is_execution_cancelled(thread_id):
                    logger.info(f"[Concurrency] Aborting graph stream for thread {thread_id}")
                    yield "event: close\ndata: {}\n\n"
                    return
                    
                seq_id += 1
                payload = {
                    "seq_id": seq_id,
                    "state": json.loads(self._serialize_state(state_val))
                }
                yield f"data: {json.dumps(payload)}\n\n"
                
            yield "event: close\ndata: {}\n\n"
        except Exception as e:
            logger.error(f"Error during graph execution: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'detail': str(e)})}\n\n"

    def continue_graph_execution(self, thread_id: str, user_message: str) -> Generator[str, None, None]:
        """
        Resumes LangGraph execution from a checkpoint using thread_id.
        Injects cancel checkpoints and sequence IDs.
        """
        # First request cancellation of any active thread to avoid concurrent writes
        request_cancel_execution(thread_id)
        clear_cancel_flag(thread_id)

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
        ).model_dump(mode="json")
        
        current_messages = state_values.get("messages", [])
        updated_messages = current_messages + [new_msg]
        
        # If the graph has already finished (next is empty), Pregel.stream(None) will exit immediately.
        # To trigger a new loop, we must pass the state update as input directly to stream().
        input_data = {"messages": updated_messages} if not current_state_dict.next else None
        
        if current_state_dict.next:
            app.update_state(config, {"messages": updated_messages})

        try:
            seq_id = 0
            for state_val in app.stream(input_data, config=config, stream_mode="values"):
                # Concurrency check
                if is_execution_cancelled(thread_id):
                    logger.info(f"[Concurrency] Aborting graph stream for thread {thread_id}")
                    yield "event: close\ndata: {}\n\n"
                    return

                seq_id += 1
                payload = {
                    "seq_id": seq_id,
                    "state": json.loads(self._serialize_state(state_val))
                }
                yield f"data: {json.dumps(payload)}\n\n"
                
            yield "event: close\ndata: {}\n\n"
        except Exception as e:
            logger.error(f"Error during graph execution: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'detail': str(e)})}\n\n"

    def retry_graph_execution(self, thread_id: str) -> Generator[str, None, None]:
        """
        Retries LangGraph execution from the last checkpoint without adding new messages.
        Injects cancel checkpoints and sequence IDs.
        """
        request_cancel_execution(thread_id)
        clear_cancel_flag(thread_id)

        app = get_resume_agent_app()
        config = {"configurable": {"thread_id": thread_id}}
        
        # Load current state from checkpointer
        current_state_dict = app.get_state(config)
        if not current_state_dict or not current_state_dict.values:
            yield f"event: error\ndata: {json.dumps({'detail': 'No active session found for this resume.'})}\n\n"
            return
            
        try:
            seq_id = 0
            for state_val in app.stream(None, config=config, stream_mode="values"):
                # Concurrency check
                if is_execution_cancelled(thread_id):
                    logger.info(f"[Concurrency] Aborting graph stream retry for thread {thread_id}")
                    yield "event: close\ndata: {}\n\n"
                    return

                seq_id += 1
                payload = {
                    "seq_id": seq_id,
                    "state": json.loads(self._serialize_state(state_val))
                }
                yield f"data: {json.dumps(payload)}\n\n"
                
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
