from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class ExperienceItem(BaseModel):
    role: str = Field(description="The job or internship title.")
    company: str = Field(description="The company or organization name.")
    dates: str = Field(description="The timeline of the experience.")
    location: Optional[str] = Field(default=None, description="The location (e.g., Remote, City, State).")
    bullet_points: List[str] = Field(description="Impactful bullet points describing responsibilities and learnings, tailored to the job description.")

class ExperienceSectionResponse(BaseModel):
    section: Literal["experience"] = Field(description="Must be 'experience'")
    content: List[ExperienceItem] = Field(description="The generated experience items.")
    explanation: str = Field(description="A brief explanation of how the experience was tailored.")
    gap_warning: Optional[str] = Field(default=None, description="Any warnings if critical job requirements are missing.")
    question: str = Field(description="A closing question asking the user if they approve the draft or want changes.")
