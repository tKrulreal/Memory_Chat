"""
Connection Recommendation Worker.

Triggers connection recommendation generation based on events.
"""

import asyncio
import logging
from typing import Any
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
                # Instead of blocking the OutboxWorker, run the slow LLM job in background
                asyncio.create_task(self._process_task(user_id, task_key))
            except Exception as task_err:
                logger.error(f"Failed to create task for {user_id}: {task_err}")
                async with self._lock:
                    self._pending_tasks.discard(task_key)

        except Exception as e:
            logger.error(f"Error in ConnectionRecommendationWorker: {e}")

    async def _process_task(self, user_id: uuid.UUID, task_key: str):
        from src.core.metrics import ai_job_failures_total, ai_job_duration_seconds
        try:
            # Debounce: wait before processing
            await asyncio.sleep(self._debounce_seconds)

            # Check if another task was queued after us
            if task_key not in self._pending_tasks:
                logger.debug(f"Task cancelled for user {user_id}")
                return

            with ai_job_duration_seconds.labels(worker_type="connection_worker").time():
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
                    await self._create_notifications(user_id, recommendations)

        except Exception as e:
            logger.error(f"Error in ConnectionRecommendationWorker background task: {e}")
            ai_job_failures_total.labels(worker_type="connection_worker").inc()
        finally:
            async with self._lock:
                self._pending_tasks.discard(task_key)

    async def _create_notifications(self, user_id: uuid.UUID, recommendations: list[Any]):
        """Tạo notification cho user về recommendations mới thỏa mãn cấu hình AI Hub."""
        from src.models.tag import AISystemConfig
        from src.models.user import User
        from src.services.notifications import NotificationService

        db = SessionLocal()
        try:
            user = db.get(User, user_id)
            if not user or not user.setting or not user.setting.ai_enabled:
                return

            ai_config = db.query(AISystemConfig).filter(
                AISystemConfig.user_id == user_id,
                AISystemConfig.key == "ai_settings"
            ).first()

            features = ai_config.value.get("features", {}) if (ai_config and isinstance(ai_config.value, dict)) else {}
            if features.get("recommendation") is False:
                return

            min_score_percent = 50
            notif_interval = "24h"
            if ai_config and isinstance(ai_config.value, dict):
                min_score_percent = int(ai_config.value.get("min_matching_score", 50))
                notif_interval = ai_config.value.get("notification_interval", getattr(user.setting, "ai_recommendation_interval", "24h"))

            if notif_interval == "off":
                return

            min_score = min_score_percent / 100.0

            # Filter recommendations matching threshold
            qualified_recs = [r for r in recommendations if getattr(r, "confidence", 0.0) >= min_score]
            if not qualified_recs:
                logger.info("No recommendations met the notification threshold %d%% for user %s", min_score_percent, user_id)
                return

            # Check interval limit if not realtime
            if notif_interval != "realtime":
                interval_hours_map = {"1h": 1, "6h": 6, "12h": 12, "24h": 24, "weekly": 168}
                hours = interval_hours_map.get(notif_interval, 24)
                
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)
                cutoff = now - timedelta(hours=hours)

                last_notif = db.query(Notification).filter(
                    Notification.user_id == user_id,
                    Notification.type == "MATCH_SUGGESTION"
                ).order_by(Notification.created_at.desc()).first()

                if last_notif and last_notif.created_at:
                    # Normalize tz
                    last_created = last_notif.created_at
                    if last_created.tzinfo is None:
                        last_created = last_created.replace(tzinfo=timezone.utc)
                    if last_created >= cutoff:
                        logger.info("Skipping matching notification for user %s: interval %s has not elapsed yet.", user_id, notif_interval)
                        return

            notif_service = NotificationService.get_instance()
            # Send notification for top qualified recommendations (up to 3)
            for rec in qualified_recs[:3]:
                target_user = db.get(User, rec.target_user_id)
                if not target_user:
                    continue
                match_score = int(getattr(rec, "confidence", 0.5) * 100)
                notif_service.send_matching_notification(
                    db=db,
                    user_id=user_id,
                    target_user=target_user,
                    match_score=match_score,
                    recommendation_id=rec.id,
                )
                logger.info("Sent matching notification to user %s for target %s (score: %d%%)", user_id, target_user.id, match_score)

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create matching notification: {e}")
        finally:
            db.close()

    async def trigger_manual(self, user_id: uuid.UUID):
        """Trigger manual generation cho user."""
        try:
            logger.info(f"Manual trigger for user {user_id}")
            recommendations = await self._agent.generate(
                user_id=user_id,
                min_score=0.4,  # Base threshold
                limit=10,
            )
            await self._create_notifications(user_id, recommendations)
            return len(recommendations)
        except Exception as e:
            logger.error(f"Error in manual trigger: {e}")
            return 0
