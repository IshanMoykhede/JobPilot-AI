from typing import Optional
from pydantic import BaseModel

class PatentEntry(BaseModel):
    title: str
    patent_number: Optional[str] = None
    description: str
