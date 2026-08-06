import uuid

from sqlalchemy.orm import Session

from src.models.chat import Conversation
from src.repositories.base import BaseRepository
from src.schemas.enums import ConversationStatus


class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self):
        super().__init__(Conversation)

    def get_by_user_id(
        self,
        db: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: ConversationStatus | None = None,
        contact_id: uuid.UUID | None = None,
    ) -> list[Conversation]:
        query = db.query(self.model).filter(Conversation.user_id == user_id)
        if status:
            query = query.filter(Conversation.status == status.value)
        if contact_id:
            query = query.filter(Conversation.contact_id == contact_id)
        return query.order_by(Conversation.last_message_time.desc()).offset(skip).limit(limit).all()

    def count_by_user_id(
        self,
        db: Session,
        user_id: uuid.UUID,
        status: ConversationStatus | None = None,
        contact_id: uuid.UUID | None = None,
    ) -> int:
        query = db.query(self.model).filter(Conversation.user_id == user_id)
        if status:
            query = query.filter(Conversation.status == status.value)
        if contact_id:
            query = query.filter(Conversation.contact_id == contact_id)
        return query.count()


conversation_repo = ConversationRepository()
