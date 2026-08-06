import uuid
from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from src.schemas.enums import ConversationStatus


class ConversationBase(BaseModel):
    title: str
    status: ConversationStatus = ConversationStatus.OPEN


class ConversationCreate(BaseModel):
    contact_id: uuid.UUID
    title: str


class ConversationUpdate(BaseModel):
    title: str | None = None
    status: ConversationStatus | None = None


class ConversationResponse(ConversationBase):
    id: uuid.UUID
    contact_id: uuid.UUID
    user_id: uuid.UUID
    last_message_at: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("last_message_at", "last_message_time"),
    )
    last_message: str | None = None

    model_config = ConfigDict(from_attributes=True)
