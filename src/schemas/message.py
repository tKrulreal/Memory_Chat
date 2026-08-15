import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, description="Nội dung tin nhắn không được rỗng")

    model_config = ConfigDict(str_strip_whitespace=True)


class MessageCreate(MessageBase):
    client_message_id: str = Field(..., description="ID tin nhắn tạo ở client để chống trùng lặp")


class MessageResponse(MessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_user_id: uuid.UUID
    client_message_id: str | None = None
    message_type: str
    
    created_at: datetime
    edited_at: datetime | None = None
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
