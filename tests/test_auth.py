import hashlib
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core.security import create_access_token, get_user_from_token, verify_password
from src.models.user import PasswordResetToken
from src.services.auth import AuthService, UserCreate, UserLogin


def test_auth_register_and_login(db_session: Session):
    # 1. Register User
    user_data = UserCreate(email="test@auth.com", password="secretpassword", full_name="Auth Tester")

    user = AuthService.register(db_session, user_data)
    assert user.email == "test@auth.com"
    assert verify_password("secretpassword", user.password_hash) is True

    # 2. Login User
    login_data = UserLogin(email="test@auth.com", password="secretpassword")
    token_response = AuthService.login(db_session, login_data)

    assert "access_token" in token_response
    assert token_response["token_type"] == "bearer"


def test_auth_login_fail(db_session: Session):
    AuthService.register(
        db_session,
        UserCreate(email="test@auth.com", password="secretpassword", full_name="Auth Tester"),
    )
    login_data = UserLogin(email="test@auth.com", password="wrongpassword")
    with pytest.raises(HTTPException) as excinfo:
        AuthService.login(db_session, login_data)

    assert excinfo.value.status_code == 401


def test_auth_login_with_phone(db_session: Session):
    AuthService.register(
        db_session,
        UserCreate(
            email="phone@auth.com",
            password="secretpassword",
            full_name="Phone Tester",
            phone="0901234567",
        ),
    )

    token_response = AuthService.login(
        db_session,
        UserLogin(email="0901234567", password="secretpassword"),
    )
    assert "access_token" in token_response


def test_auth_legacy_sha256_login_and_auto_upgrade(db_session: Session):
    import hashlib
    from src.models.user import User

    raw_password = "password123"
    sha256_hash = hashlib.sha256(raw_password.encode("utf-8")).hexdigest()

    user = User(
        email="legacy@example.com",
        password_hash=sha256_hash,
        full_name="Legacy User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Login should succeed with sha256 fallback
    login_data = UserLogin(email="legacy@example.com", password=raw_password)
    res = AuthService.login(db_session, login_data)
    assert "access_token" in res

    # Password hash in DB should now be automatically upgraded to bcrypt
    db_session.refresh(user)
    assert user.password_hash.startswith("$2b$")
    assert verify_password(raw_password, user.password_hash) is True


def test_auth_malformed_hash_returns_401_not_500(db_session: Session):
    from src.models.user import User

    # Create user with broken/malformed bcrypt salt
    user = User(
        email="broken@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4bCgIKqWEufKH/Hy",
        full_name="Broken Hash User",
    )
    db_session.add(user)
    db_session.commit()

    login_data = UserLogin(email="broken@example.com", password="password123")
    with pytest.raises(HTTPException) as excinfo:
        AuthService.login(db_session, login_data)

    assert excinfo.value.status_code == 401


def test_password_reset_changes_password_and_invalidates_token(db_session: Session, monkeypatch):
    user = AuthService.register(
        db_session,
        UserCreate(email="reset@example.com", password="oldpassword", full_name="Reset User"),
    )
    sent_urls: list[str] = []
    monkeypatch.setattr(
        "src.services.auth.send_password_reset_email",
        lambda _recipient, reset_url: sent_urls.append(reset_url) or True,
    )
    existing_access_token = create_access_token({"sub": str(user.id), "token_version": user.token_version})

    AuthService.request_password_reset(db_session, user.email)
    token = parse_qs(urlparse(sent_urls[0]).query)["token"][0]
    saved_token = db_session.query(PasswordResetToken).one()
    assert saved_token.token_hash != token

    AuthService.reset_password(db_session, token, "newpassword")
    assert verify_password("newpassword", user.password_hash)
    assert saved_token.used_at is not None
    assert get_user_from_token(existing_access_token, db_session) is None

    with pytest.raises(HTTPException) as excinfo:
        AuthService.reset_password(db_session, token, "anotherpassword")
    assert excinfo.value.status_code == 400


def test_password_reset_rejects_expired_token(db_session: Session):
    user = AuthService.register(
        db_session,
        UserCreate(email="expired@example.com", password="oldpassword", full_name="Expired User"),
    )
    expired_token = PasswordResetToken(
        user_id=user.id,
        token_hash=hashlib.sha256("expired-token".encode("utf-8")).hexdigest(),
        expires_at=datetime.now(UTC) - timedelta(minutes=1),
    )
    db_session.add(expired_token)
    db_session.commit()

    with pytest.raises(HTTPException) as excinfo:
        AuthService.reset_password(db_session, "expired-token", "newpassword")
    assert excinfo.value.status_code == 400
