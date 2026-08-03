from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class ProjectItem(BaseModel):
    title: str = Field(description="The title of the project.")
    description: str = Field(description="A brief summary of what the project is.")
    tech_stack: List[str] = Field(description="List of technologies used.")
    role: str = Field(description="The role the candidate played in the project.")
    dates: str = Field(description="The timeline of the project.")
    github: Optional[str] = Field(default=None, description="A link to the project repository or live site.")
    bullet_points: List[str] = Field(description="Impactful bullet points describing achievements and responsibilities, tailored to the job description.")

class ProjectSectionResponse(BaseModel):
    section: Literal["projects"] = Field(description="Must be 'projects'")
    content: List[ProjectItem] = Field(description="The generated project items.")
    explanation: str = Field(description="A brief explanation of why these projects were chosen and tailored this way.")
    gap_warning: Optional[str] = Field(default=None, description="Any warnings if critical job requirements are missing from the candidate's project history.")
    question: str = Field(description="A closing question asking the user if they approve the draft or want changes.")
