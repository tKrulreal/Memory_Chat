from sqlalchemy.orm import Session

from src.repositories.event_log import event_log_repo


class EventLogService:
    @staticmethod
    def log_event(db: Session, user_id: str, event_type: str, payload: dict):
        obj_in = {
            "user_id": user_id,
            "event_type": event_type,
            "payload": payload
        }
        return event_log_repo.create(db, obj_in=obj_in)

    @staticmethod
    def list_recent(db: Session, limit: int = 100):
        return event_log_repo.list_recent(db, limit=limit)
