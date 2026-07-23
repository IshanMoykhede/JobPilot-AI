from typing import Optional
from pydantic import BaseModel

class AwardEntry(BaseModel):
    title: str
    issuer: Optional[str] = None
    description: str
