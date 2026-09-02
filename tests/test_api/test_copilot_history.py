import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from src.models.user import User, Setting
from src.models.ai import CopilotMessage


@pytest.mark.asyncio
async def test_copilot_messages_persistence_and_management(
    integration_client: AsyncClient,
    db_session: Session,
):
    # 1. Create a test user
    user = User(
        id=uuid.uuid4(),
        email="copilot_tester@example.com",
        password_hash="fake_hash",
        full_name="Copilot Tester",
    )
    db_session.add(user)
    db_session.commit()

    # Create auth token
    from src.core.security import create_access_token
    token = create_access_token(data={"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # 2. GET /api/v1/copilot/messages should be empty initially
    res_get_empty = await integration_client.get("/api/v1/copilot/messages", headers=headers)
    assert res_get_empty.status_code == 200
    assert res_get_empty.json() == []

    # 3. Post a message to Copilot
    res_post = await integration_client.post(
        "/api/v1/copilot",
        json={"query": "Xin chào Copilot!"},
        headers=headers,
    )
    assert res_post.status_code == 200
    post_data = res_post.json()
    assert "response" in post_data

    # 4. Check that messages were saved to the database
    res_get_saved = await integration_client.get("/api/v1/copilot/messages", headers=headers)
    assert res_get_saved.status_code == 200
    messages = res_get_saved.json()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Xin chào Copilot!"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == post_data["response"]

    # 5. Clear history via DELETE /api/v1/copilot/messages
    res_delete = await integration_client.delete("/api/v1/copilot/messages", headers=headers)
    assert res_delete.status_code == 200
    assert res_delete.json()["status"] == "success"

    # 6. Verify GET /api/v1/copilot/messages is empty again
    res_get_cleared = await integration_client.get("/api/v1/copilot/messages", headers=headers)
    assert res_get_cleared.status_code == 200
    assert res_get_cleared.json() == []


@pytest.mark.asyncio
async def test_in_chat_copilot_isolation_from_global(
    integration_client: AsyncClient,
    db_session: Session,
):
    """Test that In-Chat Copilot messages are isolated per conversation and separate from Global Copilot."""
    from src.models.chat import Conversation
    from src.core.security import create_access_token

    # 1. Create 2 users and a conversation
    user1 = User(
        id=uuid.uuid4(),
        email=f"user1_{uuid.uuid4().hex[:6]}@example.com",
        password_hash="fake_hash",
        full_name="User One",
    )
    user2 = User(
        id=uuid.uuid4(),
        email=f"user2_{uuid.uuid4().hex[:6]}@example.com",
        password_hash="fake_hash",
        full_name="User Two",
    )
    db_session.add_all([user1, user2])
    db_session.commit()

    u1_id, u2_id = sorted([user1.id, user2.id])
    conv = Conversation(
        id=uuid.uuid4(),
        user_a_id=u1_id,
        user_b_id=u2_id,
        type="P2P",
    )
    db_session.add(conv)
    db_session.commit()

    token1 = create_access_token(data={"sub": str(user1.id)})
    headers1 = {"Authorization": f"Bearer {token1}"}

    # 2. Post Global Copilot message (no conversation_id)
    res_global = await integration_client.post(
        "/api/v1/copilot",
        json={"query": "Global Copilot query"},
        headers=headers1,
    )
    assert res_global.status_code == 200

    # 3. Post In-Chat Copilot message (with conversation_id)
    res_in_chat = await integration_client.post(
        "/api/v1/copilot",
        json={
            "query": "In-Chat Copilot query",
            "context": {"conversation_id": str(conv.id)},
        },
        headers=headers1,
    )
    assert res_in_chat.status_code == 200

    # 4. Fetch Global messages -> Should only contain Global messages
    res_get_global = await integration_client.get("/api/v1/copilot/messages", headers=headers1)
    assert res_get_global.status_code == 200
    global_msgs = res_get_global.json()
    assert len(global_msgs) == 2
    assert global_msgs[0]["content"] == "Global Copilot query"
    assert global_msgs[0]["conversation_id"] is None

    # 5. Fetch In-Chat messages -> Should only contain In-Chat messages for this conv
    res_get_in_chat = await integration_client.get(
        f"/api/v1/copilot/messages?conversation_id={conv.id}",
        headers=headers1,
    )
    assert res_get_in_chat.status_code == 200
    in_chat_msgs = res_get_in_chat.json()
    assert len(in_chat_msgs) == 2
    assert in_chat_msgs[0]["content"] == "In-Chat Copilot query"
    assert in_chat_msgs[0]["conversation_id"] == str(conv.id)

    # 6. Delete In-Chat messages -> Global messages should remain intact
    res_del_in_chat = await integration_client.delete(
        f"/api/v1/copilot/messages?conversation_id={conv.id}",
        headers=headers1,
    )
    assert res_del_in_chat.status_code == 200

    res_get_in_chat_after = await integration_client.get(
        f"/api/v1/copilot/messages?conversation_id={conv.id}",
        headers=headers1,
    )
    assert res_get_in_chat_after.json() == []

    res_get_global_after = await integration_client.get("/api/v1/copilot/messages", headers=headers1)
    assert len(res_get_global_after.json()) == 2

