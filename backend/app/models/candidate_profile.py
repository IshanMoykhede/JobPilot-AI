import uuid
from sqlalchemy import Column, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Store the parsed resume and preferences as a flexible JSONB object
    profile_json = Column(JSONB, nullable=True)
    
    # Track whether the profile setup is fully completed
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to User model
    user = relationship("User", back_populates="candidate_profile")

    # Relationship to CandidateInsights (1:Many for historical progress)
    insights = relationship("CandidateInsights", back_populates="profile", cascade="all, delete-orphan")
