import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.models.chat import Conversation, Message
from src.repositories.conversation import ConversationRepository
from src.repositories.message import MessageRepository
from src.schemas.message import MessageCreate


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
        self, db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID, page: int, limit: int
    ) -> tuple[list[Message], int]:
        self._require_owned_conversation(db, user_id, conversation_id)
        skip = (page - 1) * limit
        return (
            self.repository.get_by_conversation_id(db, conversation_id, skip, limit),
            self.repository.count_by_conversation_id(db, conversation_id),
        )

    def create_message(
        self, db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID, data: MessageCreate, event_bus: "EventBus"
    ) -> Message:
        conversation = self._require_owned_conversation(db, user_id, conversation_id)
        
        # Check idempotency
        existing = self.repository.get_by_client_id(db, data.client_message_id)
        if existing:
            raise MessageConflictError(existing)

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
                event_type=EventType.SEND_MESSAGE,
                user_id=user_id,
                payload={"message_id": str(message.id), "content": message.content},
                conversation_id=conversation_id,
            )
            db.commit()
            db.refresh(message)
        except Exception:
            db.rollback()
            raise
        return message

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
