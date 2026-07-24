from pydantic import BaseModel, Field
from typing import List, Optional

class CoCurricularActivity(BaseModel):
    title: str = Field(description="The title or role in the co-curricular activity.")
    organization: str = Field(description="The organization or institution where the activity took place.")
    description: Optional[str] = Field(None, description="A brief description of responsibilities or achievements.")
    start_date: Optional[str] = Field(None, description="Start date (e.g. YYYY-MM or YYYY).")
    end_date: Optional[str] = Field(None, description="End date (e.g. YYYY-MM or YYYY).")

class CoCurricularGenerationResponse(BaseModel):
    user_update_message: str = Field(description="A short, conversational, and empathetic message to the user explaining what you just did to their co-curricular activities to match the job description.")
    activities: List[CoCurricularActivity]
