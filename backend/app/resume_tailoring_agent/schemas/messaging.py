from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel
from .common import ResumeSectionType

class MessageRole(str, Enum):
    USER = "USER"
    SYSTEM = "SYSTEM"
    ASSISTANT = "ASSISTANT"

class MessageType(str, Enum):
    USER_QUERY = "USER_QUERY"
    ROUTING_DECISION = "ROUTING_DECISION"
    WORKFLOW_REQUEST = "WORKFLOW_REQUEST"
    WORKFLOW_RESPONSE = "WORKFLOW_RESPONSE"
    HUMAN_INPUT_REQUEST = "HUMAN_INPUT_REQUEST"
    HUMAN_INPUT_RESPONSE = "HUMAN_INPUT_RESPONSE"
    SYSTEM_NOTIFICATION = "SYSTEM_NOTIFICATION"

class MessageSource(str, Enum):
    USER = "USER"
    INTENT_ROUTER = "INTENT_ROUTER"
    SUMMARY_GENERATOR = "SUMMARY_GENERATOR"
    PROJECT_GENERATOR = "PROJECT_GENERATOR"
    EXPERIENCE_GENERATOR = "EXPERIENCE_GENERATOR"
    SKILLS_GENERATOR = "SKILLS_GENERATOR"
    EDUCATION_GENERATOR = "EDUCATION_GENERATOR"
    CERTIFICATION_GENERATOR = "CERTIFICATION_GENERATOR"
    PDF_GENERATOR = "PDF_GENERATOR"
    SYSTEM = "SYSTEM"

class ResumeMessage(BaseModel):
    id: str
    timestamp: str
    role: MessageRole
    message_type: MessageType
    from_node: MessageSource
    to_node: MessageSource
    related_section: Optional[ResumeSectionType] = None
    content: str
    payload: Optional[Dict[str, Any]] = None
