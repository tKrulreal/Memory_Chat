import logging
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_

from src.models.database import engine
from src.models.user import User, Setting
from src.models.chat import Conversation, Message
from src.models.ai import AssistantMemory

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def scheduled_memory_refresh(app_state):
    logger.info("Running scheduled_memory_refresh...")
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    memory_worker = getattr(app_state, "memory_worker", None)
    if not memory_worker:
        return
        
    session = session_factory()
    try:
        # Check users with ai_memory_refresh_interval in ('5_mins', 'hourly', 'daily', 'weekly')
        users_with_settings = session.query(User).join(Setting).filter(
            Setting.ai_memory_refresh_interval.in_(["5_mins", "hourly", "daily", "weekly"])
        ).all()
        
        for user in users_with_settings:
            interval_str = user.setting.ai_memory_refresh_interval
            if interval_str == "weekly":
                threshold_minutes = 10080
            elif interval_str == "daily":
                threshold_minutes = 1440
            elif interval_str == "hourly":
                threshold_minutes = 60
            else:
                threshold_minutes = 5
                
            # Find their memories
            memories = session.query(AssistantMemory).filter(
                AssistantMemory.owner_user_id == user.id
            ).all()
            
            for memory in memories:
                last_time = memory.updated_at
                if last_time.tzinfo is None:
                    last_time = last_time.replace(tzinfo=timezone.utc)
                idle_minutes = (datetime.now(timezone.utc) - last_time).total_seconds() / 60
                
                if idle_minutes >= threshold_minutes:
                    # check if there are newer messages since memory updated
                    last_msg = session.query(Message).filter(
                        Message.conversation_id == memory.conversation_id,
                        Message.created_at > last_time
                    ).first()
                    
                    if last_msg:
                        logger.info("Scheduled refresh triggering for user=%s conv=%s", user.id, memory.conversation_id)
                        await memory_worker._queue_refresh(user.id, memory.conversation_id)
                        
    except Exception as e:
        logger.error("Error in scheduled_memory_refresh: %s", e)
    finally:
        session.close()

async def scheduled_daily_match_notification(app_state):
    logger.info("Running scheduled_daily_match_notification...")
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = session_factory()
    try:
        from src.models.ai import Recommendation
        from src.models.tag import AISystemConfig
        from src.models.user import User, Notification
        from src.services.notifications import NotificationService
        
        now = datetime.now(timezone.utc)
        notification_service = NotificationService.get_instance()

        users = session.query(User).all()
        for user in users:
            if not user.setting or not user.setting.ai_enabled:
                continue

            ai_config = session.query(AISystemConfig).filter(
                AISystemConfig.user_id == user.id,
                AISystemConfig.key == "ai_settings"
            ).first()

            features = ai_config.value.get("features", {}) if (ai_config and isinstance(ai_config.value, dict)) else {}
            if features.get("recommendation") is False:
                continue

            min_score_percent = 50
            notif_interval = "24h"
            if ai_config and isinstance(ai_config.value, dict):
                min_score_percent = int(ai_config.value.get("min_matching_score", 50))
                notif_interval = ai_config.value.get("notification_interval", getattr(user.setting, "ai_recommendation_interval", "24h"))

            if notif_interval == "off":
                continue

            min_score = min_score_percent / 100.0

            # Check interval cutoff
            interval_hours_map = {"1h": 1, "6h": 6, "12h": 12, "24h": 24, "weekly": 168}
            hours = interval_hours_map.get(notif_interval, 24)
            cutoff = now - timedelta(hours=hours)

            last_notif = session.query(Notification).filter(
                Notification.user_id == user.id,
                Notification.type == "MATCH_SUGGESTION"
            ).order_by(Notification.created_at.desc()).first()

            if last_notif and last_notif.created_at:
                last_created = last_notif.created_at
                if last_created.tzinfo is None:
                    last_created = last_created.replace(tzinfo=timezone.utc)
                if last_created >= cutoff:
                    continue

            # Find qualified pending recommendations
            pending_recs = session.query(Recommendation).filter(
                Recommendation.owner_user_id == user.id,
                Recommendation.status == "PENDING",
                Recommendation.confidence >= min_score
            ).order_by(Recommendation.confidence.desc()).limit(3).all()

            for rec in pending_recs:
                target = session.get(User, rec.target_user_id)
                if target:
                    match_score = int(getattr(rec, "confidence", 0.5) * 100)
                    notification_service.send_matching_notification(
                        db=session,
                        user_id=user.id,
                        target_user=target,
                        match_score=match_score,
                        recommendation_id=rec.id,
                    )
            
    except Exception as e:
        logger.error("Error in scheduled_daily_match_notification: %s", e)
    finally:
        session.close()


def setup_scheduler(app):
    """Setup and start APScheduler"""
    # memory refresh runs every 5 minutes to check for 5_mins or daily thresholds
    scheduler.add_job(
        scheduled_memory_refresh, 
        IntervalTrigger(minutes=5), 
        args=[app.state],
        id="memory_refresh_job", 
        replace_existing=True
    )
    
    # daily match notification runs every day at 08:00 AM
    scheduler.add_job(
        scheduled_daily_match_notification,
        CronTrigger(hour=8, minute=0),
        args=[app.state],
        id="daily_match_notification_job",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("APScheduler started.")
