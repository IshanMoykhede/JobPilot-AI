from typing import Optional
from pydantic import BaseModel

class InternshipEntry(BaseModel):
    company: str
    role: str
    duration: Optional[str] = None
    description: str
