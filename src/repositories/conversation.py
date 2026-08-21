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

    def get_unread_counts(self, db: Session, user_id: uuid.UUID, conversation_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
        if not conversation_ids:
            return {}
        
        from sqlalchemy import func
        from src.models.chat import Message, ConversationUserState
        
        # Get all user states
        states = db.query(ConversationUserState.conversation_id, ConversationUserState.last_read_message_id).filter(
            ConversationUserState.user_id == user_id,
            ConversationUserState.conversation_id.in_(conversation_ids)
        ).all()
        
        state_map = {state.conversation_id: state.last_read_message_id for state in states}
        
        # Prepare read times
        last_read_ids = [rid for rid in state_map.values() if rid]
        read_times = {}
        if last_read_ids:
            try:
                valid_uuids = [uuid.UUID(rid) for rid in last_read_ids]
                msgs = db.query(Message.id, Message.created_at).filter(Message.id.in_(valid_uuids)).all()
                read_times = {str(m.id): m.created_at for m in msgs}
            except ValueError:
                pass
                
        # Count unread messages
        unread_counts = {cid: 0 for cid in conversation_ids}
        
        for cid in conversation_ids:
            last_read_id = state_map.get(cid)
            last_read_time = read_times.get(last_read_id) if last_read_id else None
            
            q = db.query(func.count(Message.id)).filter(
                Message.conversation_id == cid,
                Message.sender_user_id != user_id
            )
            if last_read_time:
                q = q.filter(Message.created_at > last_read_time)
            
            unread_counts[cid] = q.scalar() or 0
            
        return unread_counts


conversation_repo = ConversationRepository()
