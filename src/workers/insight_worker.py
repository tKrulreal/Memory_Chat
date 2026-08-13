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

    def start(self):
        """Subscribe to events."""
        self._event_bus.subscribe(EventType.MEMORY_UPDATED, self._handle_memory_updated)

    async def _handle_memory_updated(self, event: ChatEvent):
        """
        Handle memory update event by generating insights.
        Expects `contact_id` in event.payload.
        """
        try:
            contact_id = event.payload.get("contact_id")
            if contact_id:
                # Convert string to UUID if needed
                if isinstance(contact_id, str):
                    try:
                        contact_id = uuid.UUID(contact_id)
                    except ValueError:
                        logger.warning(f"InsightWorker: invalid contact_id format: {contact_id}")
                        return
                logger.info(f"InsightWorker triggered by {event.event_type} for contact {contact_id}")
                insights = await self._agent.generate_insights(contact_id=contact_id)
                logger.info(f"Generated {len(insights)} insights for contact {contact_id}.")
        except Exception as e:
            logger.error(f"Error in InsightWorker._handle_memory_updated: {e}")

