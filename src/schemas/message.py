from typing import Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from src.schemas.enums import MessageRole

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, description="Nội dung tin nhắn không được rỗng")
    role: MessageRole

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
