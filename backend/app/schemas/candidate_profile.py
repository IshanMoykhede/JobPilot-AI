from enum import Enum
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

# --- Enums ---

class ExperienceLevel(str, Enum):
    fresher = "Fresher"
    zero_to_two = "0-2 Years"
    two_to_five = "2-5 Years"
    five_plus = "5+ Years"

# --- Shared Sub-Schemas ---

class ExperienceSchema(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class EducationSchema(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    year: Optional[str] = None

class ProjectSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)

class CertificationSchema(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    year: Optional[str] = None
    url: Optional[str] = None

class ContactInfoSchema(BaseModel):
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

class ResumeDataSchema(BaseModel):
    contact_info: Optional[ContactInfoSchema] = None
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceSchema] = Field(default_factory=list)
    education: List[EducationSchema] = Field(default_factory=list)
    projects: List[ProjectSchema] = Field(default_factory=list)
    certifications: List[CertificationSchema] = Field(default_factory=list)
    co_curricular_activities: List[str] = Field(default_factory=list)

class PreferencesSchema(BaseModel):
    preferred_roles: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    experience_level: ExperienceLevel

class ResumeMetadataSchema(BaseModel):
    file_name: str
    uploaded_at: datetime

# --- Endpoint 1: GET /profile/status ---

class ProfileStatusResponse(BaseModel):
    profile_exists: bool = Field(description="True if the user has completed their profile setup")

# --- Endpoint 2: POST /profile/parse-resume ---

class ParseResumeRequest(BaseModel):
    resume_text: str

class ParseResumeResponse(ResumeDataSchema):
    pass

# --- Endpoint 3: POST /profile/complete-onboarding ---

class CompleteOnboardingRequest(BaseModel):
    resume_data: ResumeDataSchema
    preferences: PreferencesSchema
    resume_metadata: ResumeMetadataSchema

# this will be in response 
class CompleteOnboardingResponse(BaseModel):
    message: str
    profile_id: UUID

# --- Endpoint 4: GET /profile/me ---

class CandidateProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    profile_json: CompleteOnboardingRequest
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
