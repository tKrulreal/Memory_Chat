import pytest
from sqlalchemy import select
from src.models import User, Contact, ContactMemory, Conversation, Message
from src.models.database import Base, SessionLocal, engine

# Create tables in the test database
Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_user_creation(db_session):
    user = User(email="test@example.com", password_hash="hash", full_name="Test User")
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.created_at is not None

def test_contact_relation(db_session):
    user = db_session.execute(select(User).filter_by(email="test@example.com")).scalar_one()
    
    contact = Contact(user_id=user.id, display_name="Friend")
    db_session.add(contact)
    db_session.commit()
    
    assert contact.id is not None
    
    memory = ContactMemory(contact_id=contact.id, summary="Good friend")
    db_session.add(memory)
    db_session.commit()
    
    assert memory.contact_id == contact.id
    
def test_conversation_relation(db_session):
    user = db_session.execute(select(User).filter_by(email="test@example.com")).scalar_one()
    contact = db_session.execute(select(Contact).filter_by(display_name="Friend")).scalar_one()
    
    conv = Conversation(user_id=user.id, contact_id=contact.id)
    db_session.add(conv)
    db_session.commit()
    
    msg = Message(conversation_id=conv.id, sender_type="USER", content="Hello!", message_type="TEXT")
    db_session.add(msg)
    db_session.commit()
    
    assert msg.conversation_id == conv.id
