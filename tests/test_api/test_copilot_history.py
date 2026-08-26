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
