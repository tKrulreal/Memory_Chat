import pytest

from src.events.types import EventType
from src.models.ai import EventLog
from src.models.chat import Conversation
from src.models.contact import Contact


@pytest.mark.asyncio
async def test_conversation_crud_and_lifecycle_events(
    authenticated_client, db_session, current_user, event_bus
):
    contact = Contact(user_id=current_user.id, display_name="Alice")
    db_session.add(contact)
    db_session.commit()

    created = await authenticated_client.post(
        "/api/v1/conversations", json={"contact_id": str(contact.id), "title": "Chat with Alice"}
    )
    assert created.status_code == 201
    conversation = created.json()
    assert conversation["status"] == "OPEN"
    assert conversation["last_message"] is None

    closed = await authenticated_client.patch(
        f"/api/v1/conversations/{conversation['id']}", json={"status": "CLOSED"}
    )
    assert closed.status_code == 200
    assert closed.json()["status"] == "CLOSED"

    repeated_close = await authenticated_client.patch(
        f"/api/v1/conversations/{conversation['id']}", json={"status": "CLOSED"}
    )
    assert repeated_close.status_code == 200

    await event_bus.join()
    event_types = [event.event_type for event in db_session.query(EventLog).all()]
    assert event_types.count(EventType.OPEN_CHAT) == 1
    assert event_types.count(EventType.CLOSE_CHAT) == 1

    deleted = await authenticated_client.delete(f"/api/v1/conversations/{conversation['id']}")
    assert deleted.status_code == 204


@pytest.mark.asyncio
async def test_conversation_list_filters_and_sorts(authenticated_client, db_session, current_user):
    contact = Contact(user_id=current_user.id, display_name="Alice")
    other_contact = Contact(user_id=current_user.id, display_name="Bob")
    db_session.add_all([contact, other_contact])
    db_session.commit()
    older = Conversation(user_id=current_user.id, contact_id=contact.id, title="Older", status="OPEN")
    newer = Conversation(user_id=current_user.id, contact_id=contact.id, title="Newer", status="CLOSED")
    other = Conversation(user_id=current_user.id, contact_id=other_contact.id, title="Other", status="OPEN")
    db_session.add_all([older, newer, other])
    db_session.commit()

    response = await authenticated_client.get(
        "/api/v1/conversations", params={"contact_id": str(contact.id), "status": "OPEN"}
    )

    assert response.status_code == 200
    assert response.json()["pagination"]["total"] == 1
    assert [item["title"] for item in response.json()["data"]] == ["Older"]


@pytest.mark.asyncio
async def test_conversation_rejects_foreign_contact_and_conversation(
    authenticated_client, db_session, other_user
):
    contact = Contact(user_id=other_user.id, display_name="Private")
    db_session.add(contact)
    db_session.commit()
    conversation = Conversation(user_id=other_user.id, contact_id=contact.id, title="Private")
    db_session.add(conversation)
    db_session.commit()

    create = await authenticated_client.post(
        "/api/v1/conversations", json={"contact_id": str(contact.id), "title": "No access"}
    )
    detail = await authenticated_client.get(f"/api/v1/conversations/{conversation.id}")

    assert create.status_code == 403
    assert detail.status_code == 403
