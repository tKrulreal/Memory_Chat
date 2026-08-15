import uuid
from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from src.schemas.enums import ConversationStatus

class ParticipantResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None = None
    avatar: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ConversationBase(BaseModel):
    status: ConversationStatus = ConversationStatus.OPEN


class ConversationCreate(BaseModel):
    target_user_id: uuid.UUID | None = None
    peer_email: str | None = None


class ConversationUpdate(BaseModel):
    status: ConversationStatus | None = None


class ConversationResponse(ConversationBase):
    id: uuid.UUID
    user_a_id: uuid.UUID
    user_b_id: uuid.UUID
    
    last_message_at: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("last_message_at", "last_message_time"),
    )
    last_message: str | None = Field(
        default=None,
        validation_alias=AliasChoices("last_message", "last_message_content"),
    )
    
    user_a: ParticipantResponse | None = None
    user_b: ParticipantResponse | None = None

    model_config = ConfigDict(from_attributes=True)
