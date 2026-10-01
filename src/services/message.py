import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from src.models.chat import Conversation, Message
from src.repositories.conversation import ConversationRepository
from src.repositories.message import MessageRepository
from src.schemas.message import MessageCreate

if TYPE_CHECKING:
    from src.events.bus import EventBus


class MessageNotFoundError(Exception):
    pass


class MessageConversationNotFoundError(Exception):
    pass


class MessageOwnershipError(Exception):
    pass


class MessageConflictError(Exception):
    def __init__(self, message: Message):
        self.message = message


class MessageService:
    def __init__(self, repository: MessageRepository, conversation_repository: ConversationRepository):
        self.repository = repository
        self.conversation_repository = conversation_repository

    def list_messages(
        self,
        db: Session,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        limit: int,
        before_created_at=None,
        before_id=None,
    ) -> tuple[list[Message], bool]:
        self._require_owned_conversation(db, user_id, conversation_id)
        # Fetch limit + 1 to determine if there are more messages
        messages = self.repository.get_by_cursor(
            db, conversation_id, limit + 1, before_created_at, before_id
        )
        has_next = len(messages) > limit
        if has_next:
            messages.pop()
        return messages, has_next

    def create_message(
        self, db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID, data: MessageCreate, event_bus: "EventBus"
    ) -> tuple[Message, bool]:
        from src.core.metrics import message_delivery_latency_seconds, message_send_failures_total
        
        with message_delivery_latency_seconds.time():
            conversation = self._require_owned_conversation(db, user_id, conversation_id)
            
            # Check idempotency
            existing = self.repository.get_by_client_id(db, data.client_message_id)
            if existing:
                return existing, False  # Return tuple: (message, is_new)

            message = Message(
                conversation_id=conversation_id,
                sender_user_id=user_id,
                client_message_id=data.client_message_id,
                content=data.content,
                message_type="TEXT",
            )
            conversation.last_message_id = str(data.client_message_id)
            # Trim content if it exceeds 1024 chars to avoid DB error
            conversation.last_message_content = data.content[:1024] if data.content else None
            conversation.last_message_time = datetime.now(UTC)
            try:
                db.add_all([message, conversation])
                db.flush() # Lấy message.id trước khi commit
                from src.events.types import EventType
                event_bus.publish(
                    db=db,
                    event_type=EventType.NEW_MESSAGE,
                    user_id=user_id,
                    payload={"message_id": str(message.id), "content": message.content},
                    conversation_id=conversation_id,
                )
                
                # Mark sender's own messages as read
                from src.models.chat import ConversationUserState
                state = db.query(ConversationUserState).filter(
                    ConversationUserState.user_id == user_id,
                    ConversationUserState.conversation_id == conversation_id
                ).first()
                if not state:
                    state = ConversationUserState(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        last_read_message_id=str(message.id)
                    )
                    db.add(state)
                else:
                    state.last_read_message_id = str(message.id)
                    
                db.commit()
                db.refresh(message)
            except Exception:
                message_send_failures_total.inc()
                db.rollback()
                raise
            return message, True

    def get_owned_message(self, db: Session, user_id: uuid.UUID, message_id: uuid.UUID) -> Message:
        message = self.repository.get(db, id=message_id)
        if message is None:
            raise MessageNotFoundError
        self._require_owned_conversation(db, user_id, message.conversation_id)
        return message

    def delete_message(self, db: Session, user_id: uuid.UUID, message_id: uuid.UUID) -> Message:
        message = self.get_owned_message(db, user_id, message_id)
        if message.sender_user_id != user_id:
            raise MessageOwnershipError("Only the sender can recall this message")
        message.deleted_at = datetime.now(UTC)
        db.commit()
        db.refresh(message)
        return message

    def _require_owned_conversation(
        self, db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID
    ) -> Conversation:
        conversation = self.conversation_repository.get(db, id=conversation_id)
        if conversation is None:
            raise MessageConversationNotFoundError
        if user_id not in (conversation.user_a_id, conversation.user_b_id):
            raise MessageOwnershipError
        return conversation
