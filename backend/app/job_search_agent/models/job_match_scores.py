import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class JobMatchScore(Base):
    """
    Mapping table that connects a JobSearch session to a JobKnowledge entity.
    Stores the scores and explanations specific to that search/candidate.
    """
    __tablename__ = "job_match_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    job_search_id = Column(UUID(as_uuid=True), ForeignKey("job_searches.id", ondelete="CASCADE"), nullable=False, index=True)
    job_knowledge_id = Column(UUID(as_uuid=True), ForeignKey("job_knowledge.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Scores
    semantic_score = Column(Float, nullable=True)
    deterministic_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    
    # Quick UI Badges (so we don't need to parse the explanation)
    matching_skills = Column(JSONB, nullable=True)
    missing_skills = Column(JSONB, nullable=True)
    
    # Lazy Loaded Explanation (null until requested)
    ai_explanation = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    job_search = relationship("JobSearch")
    job_knowledge = relationship("JobKnowledge")
