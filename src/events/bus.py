import logging
import uuid
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

from sqlalchemy.orm import Session

from src.events.types import EventType
from src.models.ai import OutboxEvent

logger = logging.getLogger(__name__)


class EventBus:
    """
    EventBus sử dụng pattern Transactional Outbox.
    Mọi thao tác publish sẽ tạo một bản ghi OutboxEvent vào database
    trong cùng một transaction với thao tác chính (người gọi cần tự commit).
    """

    def __init__(self):
        self._handlers: dict[EventType, list[Callable]] = defaultdict(list)

    def publish(
        self,
        db: Session,
        event_type: EventType,
        user_id: uuid.UUID,
        payload: dict[str, Any],
        conversation_id: uuid.UUID | None = None,
    ) -> None:
        """
        Ghi một sự kiện vào bảng outbox_events.
        Lưu ý: `db` chưa được commit ở đây, nó sẽ được commit bởi caller.
        """
        full_payload = {
            "user_id": str(user_id),
            "conversation_id": str(conversation_id) if conversation_id else None,
            **payload,
        }
        event = OutboxEvent(
            event_type=event_type.value,
            payload=full_payload,
            status="PENDING",
        )
        db.add(event)
        logger.debug("Added OutboxEvent %s (user_id=%s) to session", event_type.value, user_id)

    def subscribe(self, event_type: EventType, handler: Callable[[Any], Awaitable[None] | None]) -> None:
        """Đăng ký handler cho một EventType."""
        self._handlers[event_type].append(handler)

    def get_handlers(self, event_type: EventType) -> list[Callable]:
        return self._handlers.get(event_type, [])
