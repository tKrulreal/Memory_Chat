import uuid

from sqlalchemy.orm import Session

from src.models.chat import Conversation
from src.repositories.conversation import ConversationRepository
from src.schemas.conversation import ConversationCreate, ConversationUpdate
from src.schemas.enums import ConversationStatus


class ConversationNotFoundError(Exception):
    pass


class ConversationOwnershipError(Exception):
    pass


class ConversationDuplicateError(Exception):
    pass


class ConversationService:
    def __init__(self, repository: ConversationRepository):
        self.repository = repository
        self.conversation_repository = repository

    def list_conversations(
        self,
        db: Session,
        user_id: uuid.UUID,
        page: int,
        limit: int,
        status: ConversationStatus | None = None,
    ) -> tuple[list[Conversation], int]:
        skip = (page - 1) * limit
        conversations = self.repository.get_by_user_id(db, user_id, skip, limit, status)
        total = self.repository.count_by_user_id(db, user_id, status)
        
        # Attach unread_count
        if conversations:
            conv_ids = [c.id for c in conversations]
            unread_counts = self.repository.get_unread_counts(db, user_id, conv_ids)
            for c in conversations:
                setattr(c, "unread_count", unread_counts.get(c.id, 0))
                
        return conversations, total

    def create_conversation(self, db: Session, user_id: uuid.UUID, data: ConversationCreate, event_bus: "EventBus") -> Conversation:
        if user_id == data.target_user_id:
            raise ValueError("Cannot create a conversation with yourself")

        existing = self.repository.get_by_users(db, user_id, data.target_user_id)
        if existing:
            return existing

        user_a, user_b = sorted([user_id, data.target_user_id])
        conversation = Conversation(
            user_a_id=user_a, user_b_id=user_b
        )
        db.add(conversation)
        db.flush()
        
        # Publish event
        from src.events.types import EventType
        event_bus.publish(
            db=db,
            event_type=EventType.OPEN_CHAT,
            user_id=user_id,
            payload={"conversation_id": str(conversation.id)},
            conversation_id=conversation.id,
        )
        db.commit()
        db.refresh(conversation)
        return conversation

    def get_owned_conversation(
        self, db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID
    ) -> Conversation:
        conversation = self.repository.get(db, id=conversation_id)
        if conversation is None:
            raise ConversationNotFoundError
        if user_id not in (conversation.user_a_id, conversation.user_b_id):
            raise ConversationOwnershipError
            
        unread_counts = self.repository.get_unread_counts(db, user_id, [conversation_id])
        setattr(conversation, "unread_count", unread_counts.get(conversation.id, 0))
        return conversation

    def update_conversation(
        self,
        db: Session,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        data: ConversationUpdate,
        event_bus: "EventBus",
    ) -> tuple[Conversation, bool]:
        conversation = self.get_owned_conversation(db, user_id, conversation_id)
        was_closed = conversation.status == ConversationStatus.CLOSED.value
        values = data.model_dump(exclude_unset=True)
        if "status" in values:
            values["status"] = values["status"].value
        if values:
            for field in values:
                setattr(conversation, field, values[field])
            db.add(conversation)

        closed_now = conversation.status == ConversationStatus.CLOSED.value
        should_publish = closed_now and not was_closed

        if should_publish:
            from src.events.types import EventType
            event_bus.publish(
                db=db,
                event_type=EventType.CLOSE_CHAT,
                user_id=user_id,
                payload={"conversation_id": str(conversation.id)},
                conversation_id=conversation.id,
            )

        db.commit()
        db.refresh(conversation)
        return conversation, should_publish

    def delete_conversation(self, db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID) -> None:
        self.get_owned_conversation(db, user_id, conversation_id)
        self.repository.delete(db, conversation_id)

    def mark_as_read(self, db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID) -> None:
        self.get_owned_conversation(db, user_id, conversation_id)
        
        from src.models.chat import ConversationUserState, Message
        from sqlalchemy import desc
        
        # Get latest message
        latest_msg = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(desc(Message.created_at)).first()
        if not latest_msg:
            return
            
        state = db.query(ConversationUserState).filter(
            ConversationUserState.user_id == user_id,
            ConversationUserState.conversation_id == conversation_id
        ).first()
        
        if not state:
            state = ConversationUserState(
                user_id=user_id,
                conversation_id=conversation_id,
                last_read_message_id=str(latest_msg.id)
            )
            db.add(state)
        else:
            state.last_read_message_id = str(latest_msg.id)
            
        db.commit()
