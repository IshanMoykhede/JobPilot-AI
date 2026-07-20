import uuid
from enum import Enum
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class ConversationType(str, Enum):
    JOB_SEARCH = "JOB_SEARCH"
    GENERAL_CHAT = "GENERAL_CHAT"
    RESUME_TAILORING = "RESUME_TAILORING"
    INTERVIEW_PREPARATION = "INTERVIEW_PREPARATION"
    COMPANY_ANALYSIS = "COMPANY_ANALYSIS"

class ConversationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_profile_id = Column(UUID(as_uuid=True), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=True)
    conversation_type = Column(SQLEnum(ConversationType), default=ConversationType.GENERAL_CHAT, nullable=False)
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    messages = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )
