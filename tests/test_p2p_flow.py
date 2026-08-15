import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.main import app
from src.api.deps import get_db, get_event_bus
from src.core.security import get_current_user
from src.core.security import create_access_token

@pytest.fixture
def sync_client(db_session: Session, event_bus):
    """Synchronous test client suitable for websocket testing."""
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_event_bus] = lambda: event_bus
    
    with TestClient(app) as client:
        yield client
        
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_p2p_flow_e2e(
    integration_client, db_session: Session, user_factory, sync_client
):
    """
    Test toàn bộ luồng P2P:
    - User A tạo DM với User B
    - User B tạo DM với User A (đảm bảo ra cùng ID)
    - Unauthorized third user bị reject
    - Gửi tin nhắn qua REST (Idempotency)
    - Test WebSockets realtime
    """
    # 1. Setup 3 Users
    user_a = user_factory("usera@example.com")
    user_b = user_factory("userb@example.com")
    user_c = user_factory("attacker@example.com")
    
    # 2. Get tokens
    token_a = create_access_token({"sub": str(user_a.id)})
    token_b = create_access_token({"sub": str(user_b.id)})
    token_c = create_access_token({"sub": str(user_c.id)})
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    headers_c = {"Authorization": f"Bearer {token_c}"}

    # 3. User A tạo DM tới User B
    res_a = await integration_client.post(
        "/api/v1/direct-conversations",
        json={"target_user_id": str(user_b.id)},
        headers=headers_a
    )
    assert res_a.status_code in (200, 201)
    conv_id_1 = res_a.json()["id"]

    # 4. User B tạo DM tới User A (Phải ra cùng ID - Canonical)
    res_b = await integration_client.post(
        "/api/v1/direct-conversations",
        json={"target_user_id": str(user_a.id)},
        headers=headers_b
    )
    assert res_b.status_code in (200, 201)
    conv_id_2 = res_b.json()["id"]
    assert conv_id_1 == conv_id_2, "Idempotency create direct conversation failed"

    # 5. User C cố gắng truy cập DM của A và B (Unauthorized Access)
    res_c_get = await integration_client.get(
        f"/api/v1/direct-conversations/{conv_id_1}",
        headers=headers_c
    )
    assert res_c_get.status_code == 403

    res_c_post = await integration_client.post(
        f"/api/v1/direct-conversations/{conv_id_1}/messages",
        json={"content": "I am hacking", "client_message_id": str(uuid.uuid4())},
        headers=headers_c
    )
    assert res_c_post.status_code == 403

    # 6. Test WebSocket for Realtime Delivery
    # Get WS Ticket for User B
    ticket_res = await integration_client.post("/api/v1/auth/ws-ticket", headers=headers_b)
    assert ticket_res.status_code == 200
    ticket = ticket_res.json()["ticket"]

    # Connect WebSocket for User B using sync TestClient
    with sync_client.websocket_connect(f"/ws/chat?ticket={ticket}") as websocket_b:
        # User A sends a message via REST
        client_msg_id = str(uuid.uuid4())
        msg_payload = {
            "content": "Hello B from A",
            "client_message_id": client_msg_id
        }
        res_msg_a = await integration_client.post(
            f"/api/v1/direct-conversations/{conv_id_1}/messages",
            json=msg_payload,
            headers=headers_a
        )
        assert res_msg_a.status_code in (200, 201)
        msg_data = res_msg_a.json()
        assert msg_data["content"] == "Hello B from A"
        assert msg_data["sender_user_id"] == str(user_a.id)
        
        # Test Idempotency (Sending same message again)
        res_msg_a_retry = await integration_client.post(
            f"/api/v1/direct-conversations/{conv_id_1}/messages",
            json=msg_payload,
            headers=headers_a
        )
        assert res_msg_a_retry.status_code == 409

        # User B should receive it via WS
        # The WS manager will fanout the message
        # We need to manually simulate the event bus outbox or we can just see that the REST API returned 200
        # Wait, the event bus is an Outbox now! 
        # Sending a message via REST only puts an event in `outbox_events` table.
        # It doesn't instantly broadcast via WS! 
        # The outbox_worker must process it. 
        # In this test, we must manually process the outbox, or we just test WS manually.
        
        # Actually, in Phase 3, WS was modified to broadcast directly in REST API? 
        # Let's check `messages.py`:
        # `from src.api.ws import manager; await manager.broadcast_to_user(...)`
        # Yes! The REST API directly broadcasts to the WS manager!
        # So we should immediately receive it.
        
        ws_msg = websocket_b.receive_json()
        assert ws_msg["type"] == "NEW_MESSAGE"
        assert ws_msg["content"] == "Hello B from A"

    print("All P2P Flow tests passed!")
