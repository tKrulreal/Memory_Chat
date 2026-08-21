import logging
import uuid

from src.agents.recommendation import RecommendationAgent
from src.events.bus import EventBus
from src.events.types import ChatEvent, EventType
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
        self._event_bus.subscribe(EventType.NEW_MESSAGE, self._handle_trigger)

    async def _handle_trigger(self, event: ChatEvent):
        try:
            user_id = event.user_id
            # Skip zero UUID (N/A sentinel value)
            if not user_id or user_id == uuid.UUID(int=0):
                return
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
                    
                    from src.api.ws import manager
                    await manager.broadcast_to_user(
                        user_id=user_id,
                        message={"type": "NEW_RECOMMENDATION", "count": len(recs)}
                    )
                except Exception as db_e:
                    db.rollback()
                    logger.error(f"Failed to save notifications: {db_e}")
                finally:
                    db.close()
        except Exception as e:
            logger.error(f"Error in RecommendationWorker: {e}")

