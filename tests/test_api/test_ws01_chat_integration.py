import pytest

from src.models.ai import EventLog


@pytest.mark.asyncio
async def test_ws01_auth_integrates_with_chat_workflow(integration_client, db_session, event_bus):
    registered = await integration_client.post(
        "/api/v1/auth/register",
        json={"email": "chat@example.com", "password": "secretpassword", "full_name": "Chat User"},
    )
    assert registered.status_code == 200

    logged_in = await integration_client.post(
        "/api/v1/auth/login", json={"email": "chat@example.com", "password": "secretpassword"}
    )
    assert logged_in.status_code == 200
    headers = {"Authorization": f"Bearer {logged_in.json()['access_token']}"}

    contact = await integration_client.post("/api/v1/contacts", headers=headers, json={"name": "Alice"})
    assert contact.status_code == 201

    conversation = await integration_client.post(
        "/api/v1/conversations",
        headers=headers,
        json={"contact_id": contact.json()["id"], "title": "Chat with Alice"},
    )
    assert conversation.status_code == 201

    message = await integration_client.post(
        f"/api/v1/conversations/{conversation.json()['id']}/messages",
        headers=headers,
        json={"content": "Hello", "role": "USER"},
    )
    assert message.status_code == 201

    await event_bus.join()
    assert {event.event_type for event in db_session.query(EventLog).all()} == {"OPEN_CHAT", "SEND_MESSAGE"}
