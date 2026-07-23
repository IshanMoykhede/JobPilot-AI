from typing import Optional
from pydantic import BaseModel

class WorkshopEntry(BaseModel):
    title: str
    organizer: Optional[str] = None
    description: str
