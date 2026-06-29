import uuid
from sqlalchemy import Column, String, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, index=True, nullable=False)
    otp = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
