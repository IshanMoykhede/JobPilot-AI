from typing import Optional, List
from pydantic import BaseModel, Field

class ProjectEntry(BaseModel):
    title: str
    description: str
    technologies: list[str]
    highlights: list[str]
    github_url: Optional[str] = None
    live_url: Optional[str] = None

class ProjectsGenerationResponse(BaseModel):
    user_update_message: str = Field(description="A short, conversational, and empathetic message to the user explaining what you just did to their projects to match the job description.")
    projects: List[ProjectEntry]
