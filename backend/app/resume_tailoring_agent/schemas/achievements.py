from pydantic import BaseModel

class AchievementEntry(BaseModel):
    title: str
    description: str
