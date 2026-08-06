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
        self, db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID, data: MessageCreate
    ) -> Message:
        conversation = self._require_owned_conversation(db, user_id, conversation_id)
        message = Message(
            conversation_id=conversation_id,
            sender_type=data.role.value,
            content=data.content,
            message_type="TEXT",
        )
        conversation.last_message = data.content[:2048]
        conversation.last_message_time = datetime.now(UTC)
        try:
            db.add_all([message, conversation])
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

    def delete_message(self, db: Session, user_id: uuid.UUID, message_id: uuid.UUID) -> None:
        message = self.get_owned_message(db, user_id, message_id)
        self.repository.delete(db, message.id)

    def _require_owned_conversation(
        self, db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID
    ) -> Conversation:
        conversation = self.conversation_repository.get(db, id=conversation_id)
        if conversation is None:
            raise MessageConversationNotFoundError
        if conversation.user_id != user_id:
            raise MessageOwnershipError
        return conversation
