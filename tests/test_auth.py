import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core.security import verify_password
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
