import uuid

from sqlalchemy.orm import Session

from src.models.chat import Message
from src.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    def __init__(self):
        super().__init__(Message)

    def get_by_conversation_id(
        self, db: Session, conversation_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Message]:
        return (
            db.query(self.model)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_conversation_id(self, db: Session, conversation_id: uuid.UUID) -> int:
        return db.query(self.model).filter(Message.conversation_id == conversation_id).count()

    def get_by_client_id(self, db: Session, client_message_id: str) -> Message | None:
        return db.query(self.model).filter(Message.client_message_id == client_message_id).first()


message_repo = MessageRepository()
