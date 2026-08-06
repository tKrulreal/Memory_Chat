from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker
from starlette.websockets import WebSocketDisconnect

from src.api.deps import get_db, get_websocket_event_bus
from src.core.security import create_access_token
from src.events.types import EventType
from src.main import app
from src.models.chat import Conversation, Message
from src.models.contact import Contact


class RecordingEventBus:
    def __init__(self):
        self.events = []

    async def publish(self, event_type, user_id, payload, conversation_id):
        self.events.append((event_type, user_id, payload, conversation_id))


def test_websocket_persists_and_broadcasts_to_two_clients(db_session: Session, current_user):
    contact = Contact(user_id=current_user.id, display_name="Alice")
    db_session.add(contact)
    db_session.commit()
    conversation = Conversation(user_id=current_user.id, contact_id=contact.id, title="Chat")
    db_session.add(conversation)
    db_session.commit()
    event_bus = RecordingEventBus()
    test_session_factory = sessionmaker(bind=db_session.get_bind())

    def get_test_db() -> Generator[Session]:
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_websocket_event_bus] = lambda: event_bus
    token = create_access_token({"sub": str(current_user.id)})
    try:
        with TestClient(app) as client:
            path = f"/ws/chat/{conversation.id}?token={token}"
            with client.websocket_connect(path) as first_client, client.websocket_connect(path) as second_client:
                first_client.send_json({"content": "Hello"})
                first_message = first_client.receive_json()
                second_message = second_client.receive_json()

        assert first_message["content"] == "Hello"
        assert second_message == first_message
        assert db_session.query(Message).filter_by(conversation_id=conversation.id).count() == 1
        assert event_bus.events[0][0] is EventType.SEND_MESSAGE
        assert event_bus.events[0][3] == conversation.id
    finally:
        app.dependency_overrides.clear()


def test_websocket_rejects_invalid_token(db_session: Session, current_user):
    contact = Contact(user_id=current_user.id, display_name="Alice")
    db_session.add(contact)
    db_session.commit()
    conversation = Conversation(user_id=current_user.id, contact_id=contact.id, title="Chat")
    db_session.add(conversation)
    db_session.commit()

    with TestClient(app) as client, pytest.raises(WebSocketDisconnect) as exception:
        with client.websocket_connect(f"/ws/chat/{conversation.id}?token=invalid"):
            pass

    assert exception.value.code == 1008
