from typing import Optional, List
from pydantic import BaseModel, Field

class CertificationEntry(BaseModel):
    name: str
    issuer: str
    issue_date: Optional[str] = None
    credential_url: Optional[str] = None

class CertificationsGenerationResponse(BaseModel):
    user_update_message: str = Field(description="A short, conversational, and empathetic message to the user explaining what you just did to their certifications to match the job description.")
    certifications: List[CertificationEntry]
