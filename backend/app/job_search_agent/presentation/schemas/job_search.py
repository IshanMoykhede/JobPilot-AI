from pydantic import BaseModel
from typing import List, Optional
from app.job_search_agent.explanation.schemas.explanation import ActionItem

class JobMetadataDTO(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    work_mode: Optional[str] = None
    apply_url: Optional[str] = None

class JobMatchDTO(BaseModel):
    score: float
    confidence: Optional[str] = None
    application_decision: Optional[str] = None
    score_color: str = "text-jp-accent"
    score_badge: str = "jp-badge-accent"
    progress_variant: str = "accent"

class JobGuidanceDTO(BaseModel):
    overall_fit: str
    strengths: List[str] = []
    skill_gaps: List[str] = []
    next_steps: List[ActionItem] = []
    resume_focus_areas: List[str] = []
    interview_focus_areas: List[str] = []
    experience_assessment: str
    education_assessment: str
    application_reason: str

class JobActionsDTO(BaseModel):
    can_tailor_resume: bool = True
    can_prepare_interview: bool = True
    has_skill_gaps: bool = False
    has_resume_recommendations: bool = False

class JobCardResponse(BaseModel):
    job_id: str
    job: JobMetadataDTO
    match: JobMatchDTO
    guidance: JobGuidanceDTO
    actions: JobActionsDTO

class SearchStatisticsDTO(BaseModel):
    total_jobs: int
    top_matches: int
    average_match_score: float
    highest_match_score: float
    lowest_match_score: float

class JobSearchPayloadDTO(BaseModel):
    query_title: str
    statistics: SearchStatisticsDTO
    jobs: List[JobCardResponse]

class JobSearchResponse(BaseModel):
    conversation_id: str
    workspace_id: str
    agent: str = "job_search"
    payload: JobSearchPayloadDTO
