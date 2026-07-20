import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base

class JobKnowledgeStatus(enum.Enum):
    RAW = "RAW"
    EXTRACTED = "EXTRACTED"
    FAILED = "FAILED"

class JobKnowledge(Base):
    """
    Represents the structured knowledge of a job posting.
    Deduplicated across searches using the job_hash.
    """
    __tablename__ = "job_knowledge"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_hash = Column(String, unique=True, index=True, nullable=False)
    
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    apply_url = Column(String, nullable=True)
    
    required_technologies = Column(JSONB, nullable=True)
    preferred_technologies = Column(JSONB, nullable=True)
    capabilities = Column(JSONB, nullable=True)
    
    # Store the full Pydantic model dump from the LLM to prevent data loss on cache hits
    raw_knowledge = Column(JSONB, nullable=True)
    
    processing_status = Column(SAEnum(JobKnowledgeStatus), default=JobKnowledgeStatus.RAW, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
