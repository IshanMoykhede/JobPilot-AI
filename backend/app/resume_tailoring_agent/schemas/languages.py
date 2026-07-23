from typing import Optional
from pydantic import BaseModel

class LanguageEntry(BaseModel):
    language: str
    proficiency: Optional[str] = None
