import uuid

from sqlalchemy.orm import Session

from src.models.chat import Message
from src.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    def __init__(self):
        super().__init__(Message)

    def get_by_cursor(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        limit: int = 50,
        before_created_at=None,
        before_id=None,
    ) -> list[Message]:
        query = db.query(self.model).filter(Message.conversation_id == conversation_id)
        if before_created_at and before_id:
            from sqlalchemy import tuple_
            query = query.filter(
                tuple_(Message.created_at, Message.id) < tuple_(before_created_at, before_id)
            )
        
        return (
            query
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(limit)
            .all()
        )

    def count_by_conversation_id(self, db: Session, conversation_id: uuid.UUID) -> int:
        return db.query(self.model).filter(Message.conversation_id == conversation_id).count()

    def get_by_client_id(self, db: Session, client_message_id: str) -> Message | None:
        return db.query(self.model).filter(Message.client_message_id == client_message_id).first()


message_repo = MessageRepository()
