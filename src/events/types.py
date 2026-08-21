import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
class EventType(StrEnum):
    # Real-time WebSocket standard events
    NEW_MESSAGE = "NEW_MESSAGE"
    MESSAGE_RECALLED = "MESSAGE_RECALLED"
    MESSAGE_UPDATED = "MESSAGE_UPDATED"
    TYPING = "TYPING"
    READ_RECEIPT = "READ_RECEIPT"
    CONNECTION_REQUEST = "CONNECTION_REQUEST"

    # AI/Internal events
    OPEN_CHAT = "OPEN_CHAT"
    CLOSE_CHAT = "CLOSE_CHAT"
    MEMORY_REFRESH = "MEMORY_REFRESH"
    MEMORY_UPDATED = "MEMORY_UPDATED"
    OPEN_AI = "OPEN_AI"
    NEW_RECOMMENDATION = "NEW_RECOMMENDATION"



@dataclass(frozen=True)
class ChatEvent:
    event_type: EventType
    user_id: uuid.UUID
    payload: dict[str, Any]
    conversation_id: uuid.UUID | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
