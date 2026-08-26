"""
Unit tests for Unfriend functionality and Notification synchronization.
"""

import uuid
from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException

from src.api.v1.connection_requests import (
    remove_friend_connection,
    accept_connection_request,
    reject_connection_request,
)
from src.models.user import User, Notification
from src.models.connection import ConnectionRequest
from src.models.chat import Conversation


def test_remove_friend_connection():
    """Test remove_friend_connection deletes requests and conversations."""
    db = MagicMock()
    user_a = User(id=uuid.uuid4(), email="a@test.com")
    user_b = User(id=uuid.uuid4(), email="b@test.com")

    db.get.return_value = user_b

    # Mock conversation query
    mock_conv = Conversation(id=uuid.uuid4(), user_a_id=str(user_a.id), user_b_id=str(user_b.id))
    db.query.return_value.filter.return_value.first.return_value = mock_conv

    res = remove_friend_connection(
        target_user_id=user_b.id,
        current_user=user_a,
        db=db,
    )

    assert res["target_user_id"] == str(user_b.id)
    assert db.delete.called
    assert db.commit.called


def test_cannot_unfriend_self():
    """Test that unfriending self raises 400 Bad Request."""
    db = MagicMock()
    user_a = User(id=uuid.uuid4(), email="a@test.com")

    with pytest.raises(HTTPException) as exc_info:
        remove_friend_connection(
            target_user_id=user_a.id,
            current_user=user_a,
            db=db,
        )

    assert exc_info.value.status_code == 400
    assert "Cannot unfriend yourself" in exc_info.value.detail
