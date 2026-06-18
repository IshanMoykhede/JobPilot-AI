import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class InsightStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    STALE = "STALE"

class CandidateInsights(Base):
    __tablename__ = "candidate_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_profile_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    insights_json = Column(JSONB, nullable=True)
    graph_version = Column(String, nullable=True)
    status = Column(Enum(InsightStatus), default=InsightStatus.PENDING, nullable=False, index=True)
    
    generated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship back to profile
    profile = relationship("CandidateProfile", back_populates="insights")
