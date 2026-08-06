import uuid

from sqlalchemy.orm import Session

from src.models.chat import Conversation
from src.repositories.contact import ContactRepository
from src.repositories.conversation import ConversationRepository
from src.schemas.conversation import ConversationCreate, ConversationUpdate
from src.schemas.enums import ConversationStatus


class ConversationNotFoundError(Exception):
    pass


class ConversationOwnershipError(Exception):
    pass


class ConversationContactError(Exception):
    pass


class ConversationService:
    def __init__(self, repository: ConversationRepository, contact_repository: ContactRepository):
        self.repository = repository
        self.contact_repository = contact_repository

    def list_conversations(
        self,
        db: Session,
        user_id: uuid.UUID,
        page: int,
        limit: int,
        status: ConversationStatus | None = None,
        contact_id: uuid.UUID | None = None,
    ) -> tuple[list[Conversation], int]:
        if contact_id is not None:
            self._require_owned_contact(db, user_id, contact_id)
        skip = (page - 1) * limit
        conversations = self.repository.get_by_user_id(db, user_id, skip, limit, status, contact_id)
        total = self.repository.count_by_user_id(db, user_id, status, contact_id)
        return conversations, total

    def create_conversation(self, db: Session, user_id: uuid.UUID, data: ConversationCreate) -> Conversation:
        self._require_owned_contact(db, user_id, data.contact_id)
        return self.repository.create(
            db,
            obj_in={"user_id": user_id, "contact_id": data.contact_id, "title": data.title},
        )

    def get_owned_conversation(
        self, db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID
    ) -> Conversation:
        conversation = self.repository.get(db, id=conversation_id)
        if conversation is None:
            raise ConversationNotFoundError
        if conversation.user_id != user_id:
            raise ConversationOwnershipError
        return conversation

    def update_conversation(
        self,
        db: Session,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        data: ConversationUpdate,
    ) -> tuple[Conversation, bool]:
        conversation = self.get_owned_conversation(db, user_id, conversation_id)
        was_closed = conversation.status == ConversationStatus.CLOSED.value
        values = data.model_dump(exclude_unset=True)
        if "status" in values:
            values["status"] = values["status"].value
        if values:
            conversation = self.repository.update(db, conversation, values)
        closed_now = conversation.status == ConversationStatus.CLOSED.value
        return conversation, closed_now and not was_closed

    def delete_conversation(self, db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID) -> None:
        self.get_owned_conversation(db, user_id, conversation_id)
        self.repository.delete(db, conversation_id)

    def _require_owned_contact(self, db: Session, user_id: uuid.UUID, contact_id: uuid.UUID) -> None:
        contact = self.contact_repository.get(db, id=contact_id)
        if contact is None or contact.user_id != user_id:
            raise ConversationContactError
