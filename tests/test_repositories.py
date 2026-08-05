import pytest
from sqlalchemy.orm import Session
from src.models import User, Contact
from src.models.database import Base, SessionLocal, engine
from src.repositories.contact import contact_repo

Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_contact_repository(db_session: Session):
    # 1. Setup user
    user = User(email="repo@example.com", password_hash="hash", full_name="Repo User")
    db_session.add(user)
    db_session.commit()
    
    # 2. Test create
    contact_data = {"user_id": user.id, "display_name": "Repo Contact"}
    contact = contact_repo.create(db_session, obj_in=contact_data)
    assert contact.id is not None
    assert contact.display_name == "Repo Contact"
    
    # 3. Test get
    fetched = contact_repo.get(db_session, id=contact.id)
    assert fetched is not None
    assert fetched.display_name == "Repo Contact"
    
    # 4. Test update
    updated = contact_repo.update(db_session, db_obj=contact, obj_in={"display_name": "Updated Contact"})
    assert updated.display_name == "Updated Contact"
    
    # 5. Test get_by_user_id
    user_contacts = contact_repo.get_by_user_id(db_session, user_id=user.id)
    assert len(user_contacts) == 1
    
    # 6. Test delete
    deleted = contact_repo.delete(db_session, id=contact.id)
    assert deleted is not None
    
    fetched_again = contact_repo.get(db_session, id=contact.id)
    assert fetched_again is None
