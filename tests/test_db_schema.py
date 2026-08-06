from sqlalchemy.orm import Session

from src.models import Contact, ContactMemory, Conversation, Message, User


def test_user_creation(db_session: Session):
    user = User(email="test@example.com", password_hash="hash", full_name="Test User")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.created_at is not None


def test_contact_relation(db_session: Session):
    user = User(email="test@example.com", password_hash="hash", full_name="Test User")
    db_session.add(user)
    db_session.commit()

    contact = Contact(user_id=user.id, display_name="Friend")
    db_session.add(contact)
    db_session.commit()

    assert contact.id is not None

    memory = ContactMemory(contact_id=contact.id, summary="Good friend")
    db_session.add(memory)
    db_session.commit()

    assert memory.contact_id == contact.id


def test_conversation_relation(db_session: Session):
    user = User(email="test@example.com", password_hash="hash", full_name="Test User")
    db_session.add(user)
    db_session.commit()
    contact = Contact(user_id=user.id, display_name="Friend")
    db_session.add(contact)
    db_session.commit()

    conv = Conversation(user_id=user.id, contact_id=contact.id)
    db_session.add(conv)
    db_session.commit()

    msg = Message(conversation_id=conv.id, sender_type="USER", content="Hello!", message_type="TEXT")
    db_session.add(msg)
    db_session.commit()

    assert msg.conversation_id == conv.id
