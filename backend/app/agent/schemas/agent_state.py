from typing import TypedDict, List, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session

class AgentState(TypedDict):
    """
    Global state for the LangGraph Orchestration Layer.
    Only contains orchestration references; no duplicated business logic.
    """
    conversation_id: Optional[UUID]
    workspace_id: Optional[UUID]
    candidate_profile_id: UUID
    user_query: str
    intent: Optional[str]
    messages: List[Any]
    response: Optional[Any]
    explanations: Optional[List[Any]]
    metadata: dict
