from typing import Optional, List
from pydantic import BaseModel, Field

class ExperienceEntry(BaseModel):
    company: str
    role: str
    employment_type: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    currently_working: bool
    responsibilities: list[str]
    technologies: list[str]
    achievements: list[str]

class ExperienceGenerationResponse(BaseModel):
    user_update_message: str = Field(description="A short, conversational, and empathetic message to the user explaining what you just did to their experience to match the job description.")
    experience: List[ExperienceEntry]
