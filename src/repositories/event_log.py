
from sqlalchemy.orm import Session

from src.models.ai import EventLog
from src.repositories.base import BaseRepository


class EventLogRepository(BaseRepository[EventLog]):
    def list_recent(self, db: Session, limit: int = 100) -> list[EventLog]:
        return db.query(self.model).order_by(self.model.created_at.desc()).limit(limit).all()

event_log_repo = EventLogRepository(EventLog)
