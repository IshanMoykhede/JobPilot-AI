import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base

class MarketIntelligenceCache(Base):
    __tablename__ = "market_intelligence_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String, unique=True, index=True, nullable=False)
    
    market_data_json = Column(JSONB, nullable=True)
    
    last_refreshed = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
