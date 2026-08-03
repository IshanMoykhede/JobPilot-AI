from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class ActionPriority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class ActionItem(BaseModel):
    priority: ActionPriority
    action: str

class ApplicationDecision(str, Enum):
    STRONG_APPLY = "Strong Apply"
    APPLY = "Apply"
    STRETCH_APPLY = "Stretch Apply"
    NOT_RECOMMENDED = "Not Recommended"

class JobExplanation(BaseModel):
    """
    Candidate Guidance payload output by Pipeline 5.
    Used for Frontend UI, Resume Tailoring, and Interview Preparation.
    """
    guidance_schema_version: str = "v1"
    job_id: str
    overall_fit: str
    strengths: List[str]
    skill_gaps: List[str]
    experience_assessment: str
    education_assessment: str
    application_decision: Optional[ApplicationDecision] = None
    application_reason: str
    resume_focus_areas: List[str]
    interview_focus_areas: List[str]
    next_steps: List[ActionItem]
    confidence: Optional[str] = None

class BatchJobExplanation(BaseModel):
    explanations: List[JobExplanation]
