from pydantic import BaseModel

class PositionOfResponsibilityEntry(BaseModel):
    title: str
    organization: str
    description: str
