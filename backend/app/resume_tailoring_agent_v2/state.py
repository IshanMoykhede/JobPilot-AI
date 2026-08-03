from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class ResumeTailoringState(BaseModel):
    session_id: str = Field(default="", description="Unique identifier for the current tailoring session")
    
    # Structured knowledge bases
    job_knowledge: Dict[str, Any] = Field(default_factory=dict, description="Structured requirements of the target job")
    user_knowledge: Dict[str, Any] = Field(default_factory=dict, description="Structured background of the user (raw resume, etc.)")
    
    # Workflow tracking
    pending_sections: List[str] = Field(
        default_factory=lambda: [
            "basic_info",
            "summary",
            "experience",
            "education",
            "skills",
            "projects",
            "certifications",
            "publications",
            "awards",
            "volunteer"
        ],
        description="List of sections remaining to be tailored"
    )
    current_section: Optional[str] = Field(default=None, description="The section currently being tailored")
    active_section: Optional[str] = Field(default=None, description="The section the graph should route to next")
    
    # Tailored section drafts
    drafts: Dict[str, Any] = Field(default_factory=dict, description="Stores the tailored draft content for each section")
    
    # Conversation history for feedback loops
    messages: List[Dict[str, str]] = Field(default_factory=list, description="Basic conversation history (user feedback, agent explanations)")
