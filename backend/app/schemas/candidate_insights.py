from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.models.candidate_insights import InsightStatus, ArtifactType

class CandidateInsightsBase(BaseModel):
    artifact_type: ArtifactType
    artifact_json: Optional[Dict[str, Any]] = None
    engine_version: Optional[str] = None
    status: InsightStatus = InsightStatus.PENDING

class CandidateInsightsCreate(CandidateInsightsBase):
    candidate_profile_id: UUID

class CandidateInsightsUpdate(BaseModel):
    artifact_json: Optional[Dict[str, Any]] = None
    engine_version: Optional[str] = None
    status: Optional[InsightStatus] = None
    generated_at: Optional[datetime] = None

class CandidateInsightsResponse(CandidateInsightsBase):
    id: UUID
    candidate_profile_id: UUID
    generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
