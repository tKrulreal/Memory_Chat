import logging
from typing import Dict, Any

from src.events.bus import EventBus
from src.events.types import EventType, ChatEvent
from src.agents.recommendation import RecommendationAgent
from src.models.database import SessionLocal
from src.models.user import Notification


logger = logging.getLogger(__name__)

class RecommendationWorker:
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._agent = RecommendationAgent()
        
    def subscribe(self):
        # Trigger when Memory is updated or Message is created
        self._event_bus.subscribe(EventType.MEMORY_UPDATED, self._handle_trigger)
        self._event_bus.subscribe(EventType.SEND_MESSAGE, self._handle_trigger)
        
    async def _handle_trigger(self, event: ChatEvent):
        try:
            user_id = event.user_id
            if user_id:
                logger.info(f"RecommendationWorker triggered by {event.event_type} for user {user_id}")
                recs = await self._agent.generate(user_id=user_id)
                logger.info(f"Generated {len(recs)} recommendations.")
                
                # Create Notifications for new recommendations
                if recs:
                    db = SessionLocal()
                    try:
                        for rec in recs:
                            notif = Notification(
                                user_id=user_id,
                                type="RECOMMENDATION",
                                title="New Recommendation",
                                content=f"You have a new recommendation: {rec.type} (Priority: {rec.priority})"
                            )
                            db.add(notif)
                        db.commit()
                    except Exception as db_e:
                        db.rollback()
                        logger.error(f"Failed to save notifications: {db_e}")
                    finally:
                        db.close()
        except Exception as e:
            logger.error(f"Error in RecommendationWorker: {e}")

