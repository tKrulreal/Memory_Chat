import uuid
from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from src.schemas.enums import MessageRole


class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, description="Nội dung tin nhắn không được rỗng")
    role: MessageRole = Field(validation_alias=AliasChoices("role", "sender_type"))

    model_config = ConfigDict(str_strip_whitespace=True)


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
