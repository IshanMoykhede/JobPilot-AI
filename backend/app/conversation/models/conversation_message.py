import uuid
from enum import Enum
from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, func, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Role(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"
    TOOL = "TOOL"

class MessageType(str, Enum):
    TEXT = "TEXT"
    JOB_RESULTS = "JOB_RESULTS"
    SYSTEM_EVENT = "SYSTEM_EVENT"
    TOOL_RESULT = "TOOL_RESULT"
    ERROR = "ERROR"

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLEnum(Role), nullable=False)
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT, nullable=False)
    content = Column(JSON, nullable=True)  # supports JSON payloads (Markdown, structures, UI maps)
    message_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
