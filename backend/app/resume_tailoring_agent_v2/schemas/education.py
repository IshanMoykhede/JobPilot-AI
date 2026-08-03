from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class EducationItem(BaseModel):
    degree: str = Field(description="The degree or diploma (e.g., B.S. Computer Science).")
    university: str = Field(description="The name of the institution.")
    dates: str = Field(description="Graduation date or timeline.")
    location: Optional[str] = Field(default=None, description="Location of the institution.")
    gpa: Optional[str] = Field(default=None, description="GPA or academic standing, if relevant.")
    details: Optional[List[str]] = Field(default=None, description="Key coursework, honors, or academic achievements.")

class EducationSectionResponse(BaseModel):
    section: Literal["education"] = Field(description="Must be 'education'")
    content: List[EducationItem] = Field(description="The generated education items.")
    explanation: str = Field(description="A brief explanation for the user.")
    gap_warning: Optional[str] = Field(default=None, description="Any warnings if a strictly required degree is missing.")
    question: str = Field(description="A closing question asking the user if they approve.")
