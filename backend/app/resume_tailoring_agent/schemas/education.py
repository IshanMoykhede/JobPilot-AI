from typing import Optional, List
from pydantic import BaseModel, Field

class EducationEntry(BaseModel):
    institution: str
    degree: str
    specialization: Optional[str] = None
    cgpa: Optional[float] = None
    percentage: Optional[float] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None

class EducationGenerationResponse(BaseModel):
    user_update_message: str = Field(description="A short, conversational, and empathetic message to the user explaining what you just did to their education to match the job description.")
    education: List[EducationEntry]
