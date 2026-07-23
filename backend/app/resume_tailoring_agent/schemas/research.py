from pydantic import BaseModel

class ResearchEntry(BaseModel):
    title: str
    description: str
