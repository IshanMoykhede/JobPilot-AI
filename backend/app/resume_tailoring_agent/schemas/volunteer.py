from pydantic import BaseModel

class VolunteerEntry(BaseModel):
    organization: str
    role: str
    description: str
