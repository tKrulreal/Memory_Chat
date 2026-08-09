import logging
from typing import Dict, Any

from src.events.bus import EventBus
from src.agents.recommendation import RecommendationAgent

logger = logging.getLogger(__name__)

class RecommendationWorker:
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._agent = RecommendationAgent()
        
    def subscribe(self):
        # Trigger when Memory is updated or Message is created
        self._event_bus.subscribe("memory_updated", self._handle_trigger)
        self._event_bus.subscribe("message_created", self._handle_trigger)
        
    async def _handle_trigger(self, event_type: str, data: Dict[str, Any]):
        try:
            user_id = data.get("user_id")
            if user_id:
                logger.info(f"RecommendationWorker triggered by {event_type} for user {user_id}")
                recs = await self._agent.generate(user_id=user_id)
                logger.info(f"Generated {len(recs)} recommendations.")
        except Exception as e:
            logger.error(f"Error in RecommendationWorker: {e}")
