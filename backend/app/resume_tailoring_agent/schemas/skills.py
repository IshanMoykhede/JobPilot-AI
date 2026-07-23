from pydantic import BaseModel, Field
from typing import List

class SkillCategory(BaseModel):
    category: str
    skills: list[str]

class SkillsGenerationResponse(BaseModel):
    user_update_message: str = Field(description="A short, conversational, and empathetic message to the user explaining what you just did to their skills to match the job description.")
    skills: List[SkillCategory]
