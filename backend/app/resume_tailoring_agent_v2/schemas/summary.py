from typing import Optional, Literal
from pydantic import BaseModel, Field

class SummarySectionResponse(BaseModel):
    section: Literal["summary"] = Field(description="Must be 'summary'")
    content: str = Field(description="The 2-3 sentence professional summary tailored to the job.")
    explanation: str = Field(description="A brief explanation of how the summary highlights the candidate's strengths for the role.")
    question: str = Field(description="A closing question asking the user if they approve.")
