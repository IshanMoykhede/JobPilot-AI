from pydantic import BaseModel, Field

class JobSearchRequest(BaseModel):
    query: str = Field(..., description="The natural language job search query")

class JobSearchResponse(BaseModel):
    message: str
    thread_id: str

class ResumeJobSearchResponse(BaseModel):
    message: str
    thread_id: str
