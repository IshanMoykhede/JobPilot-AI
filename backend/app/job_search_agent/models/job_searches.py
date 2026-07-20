import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class SearchStatus(enum.Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class JobSearch(Base):
    __tablename__ = "job_searches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_profile_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    original_query = Column(String, nullable=False)
    optimized_role = Column(String, nullable=True)
    optimized_location = Column(String, nullable=True)
    
    status = Column(SAEnum(SearchStatus), default=SearchStatus.PROCESSING, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
