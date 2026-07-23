from pydantic import BaseModel, Field

class ProfessionalSummary(BaseModel):
    content: str

class SummaryGenerationResponse(BaseModel):
    user_update_message: str = Field(description="A short, conversational, and empathetic message to the user explaining what you just did to their summary to match the job description. Do not use robotic language.")
    summary: ProfessionalSummary

