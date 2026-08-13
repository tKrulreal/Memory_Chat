import uuid

from sqlalchemy.orm import Session

from src.repositories.event_log import event_log_repo


class EventLogService:
    @staticmethod
    def log_event(db: Session, user_id: uuid.UUID | str, event_type: str, payload: dict):
        # Convert string to UUID if necessary
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        obj_in = {
            "user_id": user_id,
            "event_type": event_type,
            "payload": payload
        }
        return event_log_repo.create(db, obj_in=obj_in)

    @staticmethod
    def list_recent(db: Session, limit: int = 100):
        return event_log_repo.list_recent(db, limit=limit)
