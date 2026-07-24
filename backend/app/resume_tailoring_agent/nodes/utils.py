from functools import wraps
from app.resume_tailoring_agent.schemas.messaging import ResumeMessage
from app.resume_tailoring_agent.schemas.common import ResumeContent

def safe_state_node(func):
    """
    Decorator to transparently deserialize state dictionary primitives to 
    Pydantic objects on node entry, and dump them back to dict primitives 
    upon node exit. This keeps node code clean and prevents checkpoint crashes.
    """
    @wraps(func)
    def wrapper(state, *args, **kwargs):
        # 1. Unpack messages to ResumeMessage instances
        if hasattr(state, "messages") and state.messages:
            # Reconstruct list to avoid mutation side-effects during iteration
            state.messages = [
                m if isinstance(m, ResumeMessage) else ResumeMessage.model_validate(m)
                for m in state.messages
            ]
            
        # 2. Unpack resume_content to ResumeContent instances
        if hasattr(state, "resume_content") and state.resume_content is not None:
            if not isinstance(state.resume_content, ResumeContent):
                state.resume_content = ResumeContent.model_validate(state.resume_content)
                
        # 3. Call the node function
        result_state = func(state, *args, **kwargs)
        
        # 4. Pack messages back to dictionary primitives
        if hasattr(result_state, "messages") and result_state.messages:
            result_state.messages = [
                m if isinstance(m, dict) else m.model_dump(mode="json")
                for m in result_state.messages
            ]
            
        # 5. Pack resume_content back to dictionary primitives
        if hasattr(result_state, "resume_content") and result_state.resume_content is not None:
            if not isinstance(result_state.resume_content, dict):
                result_state.resume_content = result_state.resume_content.model_dump(mode="json")
                
        return result_state
    return wrapper
