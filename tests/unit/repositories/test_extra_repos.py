import pytest
from sqlalchemy.orm import Session
from src.models.database import Base, SessionLocal, engine
from src.models import User, Contact, ContactMemory
from src.repositories.memory import memory_repo
from src.repositories.recommendation import recommendation_repo
from src.repositories.event_log import event_log_repo

Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_extra_repos(db_session: Session):
    # Just basic assertions to ensure they can be imported and initialized
    assert memory_repo is not None
    assert recommendation_repo is not None
    assert event_log_repo is not None
