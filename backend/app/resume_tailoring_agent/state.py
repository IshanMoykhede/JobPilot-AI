from typing import Optional
from pydantic import BaseModel

from .schemas.common import ResumeSectionType, ResumeContent
from .schemas.messaging import ResumeMessage

class ResumeAgentState(BaseModel):
    resume_id: str
    session_id: str
    user_id: str
    messages: list[dict]
    resume_content: Optional[dict] = None
    pending_sections: list[str]
    current_section: Optional[str] = None
    job_knowledge: Optional[str] = None
    candidate_synthesis: Optional[str] = None
    user_profile_data: Optional[str] = None
    response_message: Optional[str] = None
