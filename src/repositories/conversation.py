import uuid

from sqlalchemy import or_
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
    ) -> list[Conversation]:
        query = db.query(self.model).filter(
            or_(Conversation.user_a_id == user_id, Conversation.user_b_id == user_id)
        )
        if status:
            query = query.filter(Conversation.status == status.value)
        from sqlalchemy import func
        return query.order_by(func.coalesce(Conversation.last_message_time, Conversation.created_at).desc()).offset(skip).limit(limit).all()

    def count_by_user_id(
        self,
        db: Session,
        user_id: uuid.UUID,
        status: ConversationStatus | None = None,
    ) -> int:
        query = db.query(self.model).filter(
            or_(Conversation.user_a_id == user_id, Conversation.user_b_id == user_id)
        )
        if status:
            query = query.filter(Conversation.status == status.value)
        return query.count()

    def get_by_users(self, db: Session, user_a_id: uuid.UUID, user_b_id: uuid.UUID) -> Conversation | None:
        return db.query(self.model).filter(
            or_(
                (Conversation.user_a_id == user_a_id) & (Conversation.user_b_id == user_b_id),
                (Conversation.user_a_id == user_b_id) & (Conversation.user_b_id == user_a_id)
            )
        ).first()


conversation_repo = ConversationRepository()
