from typing import Optional
from pydantic import BaseModel

class TrainingEntry(BaseModel):
    title: str
    provider: Optional[str] = None
    description: str
