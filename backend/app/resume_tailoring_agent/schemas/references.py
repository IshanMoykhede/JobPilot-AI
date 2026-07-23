from typing import Optional
from pydantic import BaseModel

class ReferenceEntry(BaseModel):
    name: str
    designation: Optional[str] = None
    organization: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
