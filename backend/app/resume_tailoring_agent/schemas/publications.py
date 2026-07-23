from typing import Optional
from pydantic import BaseModel

class PublicationEntry(BaseModel):
    title: str
    publisher: Optional[str] = None
    publication_date: Optional[str] = None
    url: Optional[str] = None
