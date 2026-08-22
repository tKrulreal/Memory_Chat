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
        from src.models.user import User
        from src.services.notifications import NotificationService
        
        # Find pending recommendations from the last 24h
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        
        recommendations = session.query(Recommendation).filter(
            Recommendation.status == "pending",
            Recommendation.created_at >= yesterday
        ).all()
        
        # Group by owner_user_id
        user_matches = {}
        for rec in recommendations:
            if rec.owner_user_id not in user_matches:
                user_matches[rec.owner_user_id] = 0
            user_matches[rec.owner_user_id] += 1
            
        notification_service = NotificationService.get_instance()
        
        for user_id, count in user_matches.items():
            logger.info("Sending daily match notification to user_id=%s (count=%d)", user_id, count)
            notification_service.create_notification(
                db=session,
                user_id=user_id,
                title="Gợi ý kết nối mới",
                content=f"Bạn có {count} gợi ý kết nối mới trong hôm nay. Hãy kiểm tra ngay!",
                type="MATCH_SUGGESTION",
                metadata={"count": count}
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
