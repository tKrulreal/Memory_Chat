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
