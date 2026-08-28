"""
Unit & Integration tests for AI Matchmaker and Notification synchronization.
"""

import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session

from src.models.user import User, Notification
from src.models.ai import Recommendation
from src.models.connection import ConnectionRequest
from src.models.chat import Conversation
from src.schemas.enums import RecommendationType
from src.services.notifications import NotificationService


def test_match_notification_sync_on_accept_recommendation(db_session: Session):
    """Test that accepting an AI recommendation syncs the MATCH_SUGGESTION notification."""
    # 1. Create 2 users
    user_a = User(
        id=uuid.uuid4(),
        email=f"user_a_{uuid.uuid4().hex[:6]}@example.com",
        full_name="User A",
        password_hash="hash",
    )
    user_b = User(
        id=uuid.uuid4(),
        email=f"user_b_{uuid.uuid4().hex[:6]}@example.com",
        full_name="User B",
        password_hash="hash",
    )
    db_session.add_all([user_a, user_b])
    db_session.commit()

    # 2. Create Recommendation
    rec = Recommendation(
        id=uuid.uuid4(),
        owner_user_id=user_a.id,
        target_user_id=user_b.id,
        type=RecommendationType.CONNECTION.value,
        status="PENDING",
        match_score=0.92,
        reason="Great match",
    )
    db_session.add(rec)

    # 3. Create Notification
    notif = Notification(
        id=uuid.uuid4(),
        user_id=user_a.id,
        type="MATCH_SUGGESTION",
        title="Gợi ý kết nối AI",
        content="Profile của User B rất phù hợp với bạn",
        data={
            "target_user_id": str(user_b.id),
            "target_name": user_b.full_name,
            "match_score": 92,
            "recommendation_id": str(rec.id),
        },
        status="UNREAD",
    )
    db_session.add(notif)
    db_session.commit()

    # 4. Call accept_connection endpoint logic
    from src.api.v1.connections import accept_connection

    result = accept_connection(
        recommendation_id=rec.id,
        current_user=user_a,
        db=db_session,
        request=None,
    )

    assert result.status == "ACCEPTED"

    # Verify notification state
    db_session.refresh(notif)
    assert notif.status == "READ"
    assert notif.data.get("action_taken") == "ACCEPTED"

    # Verify connection request created
    conn_req = db_session.query(ConnectionRequest).filter(
        ConnectionRequest.sender_id == user_a.id,
        ConnectionRequest.receiver_id == user_b.id,
    ).first()
    assert conn_req is not None
    assert conn_req.status == "PENDING"


def test_match_notification_sync_on_send_connection_request(db_session: Session):
    """Test that sending a connection request syncs the MATCH_SUGGESTION notification and Recommendation."""
    user_a = User(
        id=uuid.uuid4(),
        email=f"user_a_{uuid.uuid4().hex[:6]}@example.com",
        full_name="User A",
        password_hash="hash",
    )
    user_b = User(
        id=uuid.uuid4(),
        email=f"user_b_{uuid.uuid4().hex[:6]}@example.com",
        full_name="User B",
        password_hash="hash",
    )
    db_session.add_all([user_a, user_b])
    db_session.commit()

    rec = Recommendation(
        id=uuid.uuid4(),
        owner_user_id=user_a.id,
        target_user_id=user_b.id,
        type=RecommendationType.CONNECTION.value,
        status="PENDING",
        match_score=0.88,
        reason="Match",
    )
    db_session.add(rec)

    notif = Notification(
        id=uuid.uuid4(),
        user_id=user_a.id,
        type="MATCH_SUGGESTION",
        title="Gợi ý kết nối AI",
        content="Match",
        data={
            "target_user_id": str(user_b.id),
            "target_name": user_b.full_name,
            "match_score": 88,
            "recommendation_id": str(rec.id),
        },
        status="UNREAD",
    )
    db_session.add(notif)
    db_session.commit()

    from src.api.v1.connection_requests import send_connection_request
    from src.schemas.connection import ConnectionRequestCreate

    input_data = ConnectionRequestCreate(target_user_id=user_b.id)
    send_connection_request(
        request_in=input_data,
        current_user=user_a,
        db=db_session,
        event_bus=None,
    )

    db_session.refresh(rec)
    db_session.refresh(notif)

    assert rec.status == "ACCEPTED"
    assert notif.status == "READ"
    assert notif.data.get("action_taken") == "ACCEPTED"


@pytest.mark.asyncio
async def test_generate_connections_syncs_notifications_and_scores(db_session: Session):
    """Test that generate_connections creates matching notifications with exact same scores."""
    from unittest.mock import AsyncMock
    from src.models.user import Setting
    from src.models.tag import AISystemConfig
    from src.api.v1.connections import generate_connections

    user_a = User(
        id=uuid.uuid4(),
        email=f"user_a_{uuid.uuid4().hex[:6]}@example.com",
        full_name="User A",
        password_hash="hash",
    )
    user_b = User(
        id=uuid.uuid4(),
        email=f"user_b_{uuid.uuid4().hex[:6]}@example.com",
        full_name="User B",
        password_hash="hash",
    )
    db_session.add_all([user_a, user_b])
    db_session.commit()

    setting_a = Setting(user_id=user_a.id, ai_enabled=True)
    db_session.add(setting_a)

    cfg = AISystemConfig(
        id=uuid.uuid4(),
        user_id=user_a.id,
        key="ai_settings",
        value={"features": {"recommendation": True}, "min_matching_score": 60},
    )
    db_session.add(cfg)
    db_session.commit()

    mock_rec = Recommendation(
        id=uuid.uuid4(),
        owner_user_id=user_a.id,
        target_user_id=user_b.id,
        type="CONNECTION",
        status="PENDING",
        match_score=0.85,
        priority="HIGH",
        reason="Good synergy",
    )
    db_session.add(mock_rec)
    db_session.commit()

    mock_agent = AsyncMock()
    mock_agent.generate.return_value = [mock_rec]

    resp = await generate_connections(
        current_user=user_a,
        db=db_session,
        agent=mock_agent,
        force_refresh=False,
    )

    assert resp.generated == 1

    # Verify notification created for User A with exact score 85%
    notif = db_session.query(Notification).filter(
        Notification.user_id == user_a.id,
        Notification.type == "MATCH_SUGGESTION",
    ).first()

    assert notif is not None
    assert notif.data["target_user_id"] == str(user_b.id)
    assert notif.data["match_score"] == 85
    assert notif.data["recommendation_id"] == str(mock_rec.id)

