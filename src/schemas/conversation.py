from typing import Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.schemas.enums import ConversationStatus

class ConversationBase(BaseModel):
    title: str
    status: ConversationStatus = ConversationStatus.OPEN

class ConversationCreate(BaseModel):
    contact_id: uuid.UUID
    title: str

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[ConversationStatus] = None

class ConversationResponse(ConversationBase):
    id: uuid.UUID
    contact_id: uuid.UUID
    user_id: uuid.UUID
    last_message_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
