"""
Connection Recommendation Worker.

Triggers connection recommendation generation based on events.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta

from src.agents.connection import ConnectionRecommendationAgent
from src.events.bus import EventBus
from src.events.types import ChatEvent, EventType
from src.models.database import SessionLocal
from src.models.user import Notification

logger = logging.getLogger(__name__)


class ConnectionRecommendationWorker:
    """
    Worker để trigger connection recommendations.

    Subscribe: MEMORY_UPDATED
    Logic:
    1. Debounce để tránh spam
    2. Check nếu đủ contacts để analyze
    3. Gọi ConnectionRecommendationAgent
    4. Tạo notification cho user nếu có recommendations mới
    """

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._agent = ConnectionRecommendationAgent()
        self._pending_tasks: set[str] = set()
        self._lock = asyncio.Lock()
        self._debounce_seconds = 60  # Chờ 60 giây sau event cuối cùng

    def subscribe(self):
        """Đăng ký handler cho MEMORY_UPDATED event."""
        self._event_bus.subscribe(EventType.MEMORY_UPDATED, self._handle_trigger)
        logger.info("ConnectionRecommendationWorker subscribed to MEMORY_UPDATED")

    async def _handle_trigger(self, event: ChatEvent):
        """Handle MEMORY_UPDATED event."""
        try:
            user_id = event.user_id

            # Skip zero UUID (N/A sentinel value)
            if not user_id or user_id == uuid.UUID(int=0):
                return

            task_key = f"{user_id}"
            if task_key in self._pending_tasks:
                logger.debug(f"Task already pending for user {user_id}")
                return

            async with self._lock:
                self._pending_tasks.add(task_key)

            try:
                # Debounce: wait before processing
                await asyncio.sleep(self._debounce_seconds)

                # Check if another task was queued after us
                if task_key not in self._pending_tasks:
                    logger.debug(f"Task cancelled for user {user_id}")
                    return

                logger.info(f"ConnectionRecommendationWorker processing for user {user_id}")

                # Generate recommendations
                recommendations = await self._agent.generate(
                    user_id=user_id,
                    min_score=0.5,
                    limit=5,
                )

                logger.info(f"Generated {len(recommendations)} connection recommendations")

                # Create notification if there are new recommendations
                if recommendations:
                    await self._create_notifications(user_id, len(recommendations))

            finally:
                async with self._lock:
                    self._pending_tasks.discard(task_key)

        except Exception as e:
            logger.error(f"Error in ConnectionRecommendationWorker: {e}")

    async def _create_notifications(self, user_id: uuid.UUID, count: int):
        """Tạo notification cho user về recommendations mới."""
        db = SessionLocal()
        try:
            notification = Notification(
                user_id=user_id,
                type="CONNECTION_RECOMMENDATION",
                title="Có gợi ý kết nối mới",
                content=f"Hệ thống đã tìm thấy {count} cơ hội kết nối tiềm năng cho bạn. Nhấn để xem chi tiết.",
            )
            db.add(notification)
            db.commit()
            logger.info(f"Created notification for user {user_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create notification: {e}")
        finally:
            db.close()

    async def trigger_manual(self, user_id: uuid.UUID):
        """Trigger manual generation cho user."""
        try:
            logger.info(f"Manual trigger for user {user_id}")
            recommendations = await self._agent.generate(
                user_id=user_id,
                min_score=0.4,  # Lower threshold for manual trigger
                limit=10,
            )
            await self._create_notifications(user_id, len(recommendations))
            return len(recommendations)
        except Exception as e:
            logger.error(f"Error in manual trigger: {e}")
            return 0
