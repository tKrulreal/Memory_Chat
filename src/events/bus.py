import asyncio
import inspect
import logging
import uuid
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from src.events.types import ChatEvent, EventType
from src.models.ai import EventLog
from src.models.database import SessionLocal

logger = logging.getLogger(__name__)

EventHandler = Callable[[ChatEvent], Awaitable[None] | None]


class EventBus:
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal):
        self._session_factory = session_factory
        self._queue: asyncio.Queue[ChatEvent] = asyncio.Queue()
        self._handlers: dict[EventType, list[EventHandler]] = defaultdict(list)
        self._dispatcher: asyncio.Task[None] | None = None

    async def publish(
        self,
        event_type: EventType,
        user_id: uuid.UUID,
        payload: dict[str, Any],
        conversation_id: uuid.UUID | None = None,
    ) -> ChatEvent:
        event = ChatEvent(event_type, user_id, payload, conversation_id)
        await self._queue.put(event)
        return event

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    async def start(self) -> None:
        if self._dispatcher is None or self._dispatcher.done():
            self._dispatcher = asyncio.create_task(self.dispatcher_loop())

    async def stop(self) -> None:
        await self._queue.join()
        if self._dispatcher is not None:
            self._dispatcher.cancel()
            try:
                await self._dispatcher
            except asyncio.CancelledError:
                pass
            self._dispatcher = None

    async def join(self) -> None:
        await self._queue.join()

    async def dispatcher_loop(self) -> None:
        while True:
            event = await self._queue.get()
            try:
                self._persist(event)
                for handler in self._handlers[event.event_type]:
                    try:
                        result = handler(event)
                        if inspect.isawaitable(result):
                            await result
                    except Exception:
                        logger.exception("Event handler failed for %s", event.event_type)
            except Exception:
                logger.exception("Event dispatch failed for %s", event.event_type)
            finally:
                self._queue.task_done()

    async def list_recent(self, limit: int = 100) -> list[EventLog]:
        session = self._session_factory()
        try:
            return session.query(EventLog).order_by(EventLog.created_at.desc()).limit(limit).all()
        finally:
            session.close()

    def _persist(self, event: ChatEvent) -> None:
        session = self._session_factory()
        try:
            session.add(
                EventLog(
                    user_id=event.user_id,
                    conversation_id=event.conversation_id,
                    event_type=event.event_type.value,
                    payload=event.payload,
                )
            )
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
