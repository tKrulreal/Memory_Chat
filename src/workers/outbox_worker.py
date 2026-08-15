import asyncio
import inspect
import logging
import uuid

from sqlalchemy.orm import sessionmaker

from src.events.bus import EventBus
from src.events.types import ChatEvent, EventType
from src.models.ai import OutboxEvent
from src.models.database import SessionLocal

logger = logging.getLogger(__name__)


class OutboxWorker:
    def __init__(self, event_bus: EventBus, session_factory: sessionmaker = SessionLocal):
        self.event_bus = event_bus
        self.session_factory = session_factory
        self._running = False
        self._task: asyncio.Task | None = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _poll_loop(self):
        logger.info("OutboxWorker started polling")
        while self._running:
            try:
                await self._process_pending_events()
            except Exception as e:
                logger.exception("Error in OutboxWorker: %s", e)
            await asyncio.sleep(2)

    async def _process_pending_events(self):
        session = self.session_factory()
        try:
            # Query up to 50 pending events
            events = (
                session.query(OutboxEvent)
                .filter(OutboxEvent.status == "PENDING")
                .order_by(OutboxEvent.created_at.asc())
                .limit(50)
                .with_for_update(skip_locked=True)
                .all()
            )
            
            if not events:
                return

            for outbox_event in events:
                event_type_str = outbox_event.event_type
                try:
                    event_type = EventType(event_type_str)
                except ValueError:
                    logger.warning("Unknown event type: %s", event_type_str)
                    outbox_event.status = "FAILED"
                    continue

                payload = dict(outbox_event.payload or {})
                user_id_str = payload.pop("user_id", None)
                conversation_id_str = payload.pop("conversation_id", None)
                
                user_id = uuid.UUID(user_id_str) if user_id_str else uuid.uuid4()
                conversation_id = uuid.UUID(conversation_id_str) if conversation_id_str else None

                chat_event = ChatEvent(
                    event_type=event_type,
                    user_id=user_id,
                    payload=payload,
                    conversation_id=conversation_id,
                    id=outbox_event.id,
                    created_at=outbox_event.created_at
                )

                handlers = self.event_bus.get_handlers(event_type)
                success = True
                for handler in handlers:
                    try:
                        result = handler(chat_event)
                        if inspect.isawaitable(result):
                            await result
                    except Exception as e:
                        logger.exception("Handler for %s failed: %s", event_type_str, e)
                        success = False
                
                outbox_event.status = "PROCESSED" if success else "FAILED"
            
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
