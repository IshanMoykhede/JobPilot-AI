from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class CertificationItem(BaseModel):
    name: str = Field(description="The name of the certification.")
    issuer: str = Field(description="The organization that issued the certification.")
    date: Optional[str] = Field(default=None, description="The date it was issued or expires.")
    details: Optional[str] = Field(default=None, description="A brief one-sentence highlight of what was covered, if relevant to the job.")

class CertificationSectionResponse(BaseModel):
    section: Literal["certifications"] = Field(description="Must be 'certifications'")
    content: List[CertificationItem] = Field(description="The generated certification items.")
    explanation: str = Field(description="A brief explanation for the user.")
    gap_warning: Optional[str] = Field(default=None, description="Any warnings if a strictly required certification is missing.")
    question: str = Field(description="A closing question asking the user if they approve.")
