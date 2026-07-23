import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import String, DateTime, ForeignKey, Text, func, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

from app.resume_tailoring_agent.schemas.messaging import MessageRole, MessageType, MessageSource
from app.resume_tailoring_agent.schemas.common import ResumeSectionType

class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False, default="Untitled Resume")
    status: Mapped[str] = mapped_column(String, nullable=False, default="DRAFT")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    messages: Mapped[List["ResumeMessageModel"]] = relationship(
        "ResumeMessageModel", back_populates="resume", cascade="all, delete-orphan", order_by="ResumeMessageModel.created_at"
    )
    content: Mapped[Optional["ResumeContentModel"]] = relationship(
        "ResumeContentModel", back_populates="resume", uselist=False, cascade="all, delete-orphan"
    )

class ResumeMessageModel(Base):
    __tablename__ = "resume_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role: Mapped[MessageRole] = mapped_column(SQLAlchemyEnum(MessageRole, name="message_role_enum", create_constraint=True), nullable=False)
    message_type: Mapped[MessageType] = mapped_column(SQLAlchemyEnum(MessageType, name="message_type_enum", create_constraint=True), nullable=False)
    from_node: Mapped[MessageSource] = mapped_column(SQLAlchemyEnum(MessageSource, name="message_source_enum", create_constraint=True), nullable=False)
    to_node: Mapped[MessageSource] = mapped_column(SQLAlchemyEnum(MessageSource, name="message_source_enum", create_constraint=True), nullable=False)
    related_section: Mapped[Optional[ResumeSectionType]] = mapped_column(SQLAlchemyEnum(ResumeSectionType, name="resume_section_type_enum", create_constraint=True), nullable=True)
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    resume: Mapped["Resume"] = relationship("Resume", back_populates="messages")

class ResumeContentModel(Base):
    __tablename__ = "resume_contents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default='{}')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    resume: Mapped["Resume"] = relationship("Resume", back_populates="content")
