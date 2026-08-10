import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from src.schemas.enums import RecommendationType

class RecommendationBase(BaseModel):
    contact_id: uuid.UUID
    type: RecommendationType
    reason: str
    priority: str
    status: str

class RecommendationResponse(RecommendationBase):
    id: uuid.UUID
    created_at: datetime
    
    # Optional field if we want to return contact details alongside recommendation
    contact_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
