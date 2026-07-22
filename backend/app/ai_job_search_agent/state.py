import operator
from typing import TypedDict, Annotated, Optional, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from app.ai_job_search_agent.schemas import ActivityLog

class V2AgentState(TypedDict):
    """
    The core state object for the Job Search Agent V2.
    """
    session_id: str
    user_id: str
    
    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str
    
    intent: Optional[str]
    
    optimized_query: Optional[str]
    additional_requirements: Optional[dict[str, Any]]
    
    activity_logs: Annotated[list[ActivityLog], operator.add]
    
    structured_job_ids: list[str]
    recommended_job_ids: list[str]
    alternative_job_ids: list[str]
    
    agent_response: Optional[str]
