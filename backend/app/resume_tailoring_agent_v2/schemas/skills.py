from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class SkillCategory(BaseModel):
    category_name: str = Field(description="The name of the skill category (e.g., 'Languages', 'Frameworks', 'Cloud', 'Core Competencies')")
    skills: List[str] = Field(description="List of skills in this category")

class SkillsSectionResponse(BaseModel):
    section: Literal["skills"] = Field(description="Must be 'skills'")
    content: List[SkillCategory] = Field(description="The grouped skills to display on the resume.")
    explanation: str = Field(description="A brief explanation of how the skills were categorized.")
    gap_warning: Optional[str] = Field(default=None, description="Any critical job skills that are missing.")
    question: str = Field(description="A closing question asking the user if they approve the draft or want changes.")
