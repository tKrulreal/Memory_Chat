import pytest
from sqlalchemy.orm import Session

from src.models.contact import Contact
from src.repositories.contact import ContactRepository
from src.repositories.conversation import ConversationRepository
from src.schemas.conversation import ConversationCreate, ConversationUpdate
from src.schemas.enums import ConversationStatus
from src.services.conversation import ConversationOwnershipError, ConversationService


def test_conversation_service_creates_filters_and_closes(db_session: Session, current_user):
    contact = Contact(user_id=current_user.id, display_name="Alice")
    db_session.add(contact)
    db_session.commit()
    service = ConversationService(ConversationRepository(), ContactRepository())

    conversation = service.create_conversation(
        db_session, current_user.id, ConversationCreate(contact_id=contact.id, title="Project")
    )
    conversations, total = service.list_conversations(
        db_session, current_user.id, page=1, limit=20, status=ConversationStatus.OPEN
    )
    updated, closed_now = service.update_conversation(
        db_session,
        current_user.id,
        conversation.id,
        ConversationUpdate(status=ConversationStatus.CLOSED),
    )

    assert total == 1
    assert conversations == [conversation]
    assert updated.status == ConversationStatus.CLOSED
    assert closed_now is True


def test_conversation_service_rejects_foreign_owner(db_session: Session, current_user, other_user):
    contact = Contact(user_id=other_user.id, display_name="Private")
    db_session.add(contact)
    db_session.commit()
    service = ConversationService(ConversationRepository(), ContactRepository())
    conversation = service.create_conversation(
        db_session, other_user.id, ConversationCreate(contact_id=contact.id, title="Private")
    )

    with pytest.raises(ConversationOwnershipError):
        service.get_owned_conversation(db_session, current_user.id, conversation.id)
