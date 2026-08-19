import asyncio
import logging
import uuid

from src.agents.insight.agent import InsightAgent
from src.events.bus import EventBus
from src.events.types import ChatEvent, EventType

logger = logging.getLogger(__name__)

class InsightWorker:
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._agent = InsightAgent()
        self._pending_tasks: set[str] = set()
        self._lock = asyncio.Lock()

    def start(self):
        """Subscribe to events."""
        self._event_bus.subscribe(EventType.MEMORY_UPDATED, self._handle_memory_updated)

    async def _handle_memory_updated(self, event: ChatEvent):
        """
        Handle memory update event by spawning an insight generation task.
        """
        try:
            contact_id = event.payload.get("contact_id")
            if not contact_id:
                return
            
            # Convert string to UUID if needed
            if isinstance(contact_id, str):
                try:
                    contact_id = uuid.UUID(contact_id)
                except ValueError:
                    logger.warning(f"InsightWorker: invalid contact_id format: {contact_id}")
                    return

            task_key = str(contact_id)
            async with self._lock:
                if task_key in self._pending_tasks:
                    logger.debug(f"InsightWorker: task already pending for contact {contact_id}")
                    return
                self._pending_tasks.add(task_key)

            # Spawn background task to prevent blocking OutboxWorker
            asyncio.create_task(self._generate_insights(contact_id, task_key))
            
        except Exception as e:
            logger.error(f"Error in InsightWorker._handle_memory_updated: {e}")

    async def _generate_insights(self, contact_id: uuid.UUID, task_key: str):
        from src.core.metrics import ai_job_failures_total, ai_job_duration_seconds
        try:
            with ai_job_duration_seconds.labels(worker_type="insight_worker").time():
                logger.info(f"InsightWorker generating insights for contact {contact_id}")
                insights = await self._agent.generate_insights(contact_id=contact_id)
                logger.info(f"Generated {len(insights)} insights for contact {contact_id}.")
        except Exception as e:
            logger.error(f"Error generating insights for contact {contact_id}: {e}")
            ai_job_failures_total.labels(worker_type="insight_worker").inc()
        finally:
            async with self._lock:
                self._pending_tasks.discard(task_key)
