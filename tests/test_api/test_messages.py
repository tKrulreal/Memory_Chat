import pytest

from src.events.types import EventType
from src.models.ai import EventLog
from src.models.chat import Conversation
from src.models.contact import Contact


@pytest.mark.asyncio
async def test_message_crud_updates_conversation_and_emits_event(
    authenticated_client, db_session, current_user, event_bus
):
    contact = Contact(user_id=current_user.id, display_name="Alice")
    db_session.add(contact)
    db_session.commit()
    conversation = Conversation(user_id=current_user.id, contact_id=contact.id, title="Chat")
    db_session.add(conversation)
    db_session.commit()

    created = await authenticated_client.post(
        f"/api/v1/conversations/{conversation.id}/messages", json={"content": "Hello", "role": "USER"}
    )
    assert created.status_code == 201
    message = created.json()
    assert message["role"] == "USER"
    assert message["content"] == "Hello"

    db_session.refresh(conversation)
    assert conversation.last_message == "Hello"
    assert conversation.last_message_time is not None

    await event_bus.join()
    event_log = db_session.query(EventLog).filter_by(event_type=EventType.SEND_MESSAGE).one()
    assert event_log.conversation_id == conversation.id
    assert event_log.payload["message_id"] == message["id"]

    detail = await authenticated_client.get(f"/api/v1/messages/{message['id']}")
    assert detail.status_code == 200

    deleted = await authenticated_client.delete(f"/api/v1/messages/{message['id']}")
    assert deleted.status_code == 204


@pytest.mark.asyncio
async def test_message_list_and_ownership(authenticated_client, db_session, current_user, other_user):
    contact = Contact(user_id=current_user.id, display_name="Alice")
    foreign_contact = Contact(user_id=other_user.id, display_name="Private")
    db_session.add_all([contact, foreign_contact])
    db_session.commit()
    conversation = Conversation(user_id=current_user.id, contact_id=contact.id, title="Chat")
    foreign_conversation = Conversation(user_id=other_user.id, contact_id=foreign_contact.id, title="Private")
    db_session.add_all([conversation, foreign_conversation])
    db_session.commit()

    for content in ["One", "Two"]:
        response = await authenticated_client.post(
            f"/api/v1/conversations/{conversation.id}/messages", json={"content": content, "role": "USER"}
        )
        assert response.status_code == 201

    listed = await authenticated_client.get(f"/api/v1/conversations/{conversation.id}/messages", params={"limit": 1})
    foreign = await authenticated_client.get(f"/api/v1/conversations/{foreign_conversation.id}/messages")
    forged = await authenticated_client.post(
        f"/api/v1/conversations/{conversation.id}/messages", json={"content": "No", "role": "AI"}
    )

    assert listed.status_code == 200
    assert listed.json()["pagination"]["total"] == 2
    assert [message["content"] for message in listed.json()["data"]] == ["One"]
    assert foreign.status_code == 403
    assert forged.status_code == 422
