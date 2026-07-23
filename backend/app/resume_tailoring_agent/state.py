from typing import Optional
from pydantic import BaseModel

from .schemas.common import ResumeSectionType, ResumeContent
from .schemas.messaging import ResumeMessage

class ResumeAgentState(BaseModel):
    resume_id: str
    session_id: str
    user_id: str
    messages: list[ResumeMessage]
    resume_content: Optional[ResumeContent] = None
    pending_sections: list[ResumeSectionType]
    current_section: Optional[ResumeSectionType] = None
    job_knowledge: Optional[str] = None
    candidate_synthesis: Optional[str] = None
    response_message: Optional[str] = None
