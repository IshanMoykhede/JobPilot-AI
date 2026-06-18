from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class MarketIntelligenceCacheBase(BaseModel):
    role_name: str
    market_data_json: Optional[Dict[str, Any]] = None

class MarketIntelligenceCacheCreate(MarketIntelligenceCacheBase):
    pass

class MarketIntelligenceCacheUpdate(BaseModel):
    market_data_json: Optional[Dict[str, Any]] = None
    last_refreshed: Optional[datetime] = None

class MarketIntelligenceCacheResponse(MarketIntelligenceCacheBase):
    id: UUID
    last_refreshed: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
