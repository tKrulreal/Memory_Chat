import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class EventType(StrEnum):
    SEND_MESSAGE = "SEND_MESSAGE"
    OPEN_CHAT = "OPEN_CHAT"
    CLOSE_CHAT = "CLOSE_CHAT"
    MEMORY_REFRESH = "MEMORY_REFRESH"
    OPEN_AI = "OPEN_AI"


@dataclass(frozen=True)
class ChatEvent:
    event_type: EventType
    user_id: uuid.UUID
    payload: dict[str, Any]
    conversation_id: uuid.UUID | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
