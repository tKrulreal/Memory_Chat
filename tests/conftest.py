from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.deps import get_db, get_event_bus
from src.core.security import get_current_user
from src.events.bus import EventBus
from src.main import app
from src.models import Base, User


@pytest.fixture
def db_session() -> Generator[Session]:
    """Provide a fresh database so tests cannot affect application data."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def user_factory(db_session: Session):
    def create_user(email: str = "user@example.com") -> User:
        user = User(email=email, password_hash="hash", full_name="Test User")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return create_user


@pytest.fixture
def current_user(user_factory) -> User:
    return user_factory()


@pytest.fixture
def other_user(user_factory) -> User:
    return user_factory("other@example.com")


@pytest_asyncio.fixture
async def client():
    """Async HTTP client for testing API endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def event_bus(db_session: Session):
    return EventBus()

@pytest_asyncio.fixture
async def authenticated_client(db_session: Session, current_user: User, event_bus: EventBus):
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_event_bus] = lambda: event_bus
    app.dependency_overrides[get_current_user] = lambda: current_user
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def integration_client(db_session: Session, event_bus: EventBus):
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_event_bus] = lambda: event_bus
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def mock_llm():
    """Mock LLM to avoid calling OpenAI during tests.

    Usage in test:
        def test_something(mock_llm):
            # LLM calls will return mock response instead of hitting OpenAI
            ...
    """
    mock = AsyncMock()
    mock.ainvoke.return_value = AsyncMock(content="Mocked LLM response")
    return mock
