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
