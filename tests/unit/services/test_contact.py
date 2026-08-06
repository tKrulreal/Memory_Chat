import pytest
from sqlalchemy.orm import Session

from src.models.contact import Contact
from src.repositories.contact import ContactRepository
from src.schemas.contact import ContactCreate, ContactUpdate
from src.services.contact import ContactOwnershipError, ContactService


def test_contact_service_persists_api_field_mappings(db_session: Session, current_user):
    service = ContactService(ContactRepository())

    contact = service.create_contact(
        db_session,
        current_user.id,
        ContactCreate(name="Alice", avatar_url="https://example.com/alice.png", relationship_score=8),
    )
    assert contact.display_name == "Alice"
    assert contact.avatar == "https://example.com/alice.png"

    updated = service.update_contact(
        db_session,
        current_user.id,
        contact.id,
        ContactUpdate(name="Alice Updated", relationship_score=9),
    )

    assert updated.display_name == "Alice Updated"
    assert service.to_response(updated).relationship_score == 9


def test_contact_service_rejects_foreign_owner(db_session: Session, current_user, other_user):
    service = ContactService(ContactRepository())
    contact = Contact(user_id=other_user.id, display_name="Private")
    db_session.add(contact)
    db_session.commit()

    with pytest.raises(ContactOwnershipError):
        service.get_owned_contact(db_session, current_user.id, contact.id)
