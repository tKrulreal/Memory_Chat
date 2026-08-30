import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.config import get_settings
from src.models.user import User
from src.repositories.user import user_repo

SECRET_KEY = get_settings().jwt_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = get_settings().jwt_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

import hashlib

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except (ValueError, TypeError):
        # Fallback check for legacy SHA-256 hashes
        if hashlib.sha256(plain_password.encode('utf-8')).hexdigest() == hashed_password:
            return True
        return False
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = get_user_from_token(token, db)
    if user is None:
        raise credentials_exception
    return user


def get_user_from_token(token: str, db: Session) -> User | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = uuid.UUID(payload["sub"])
        if payload.get("type") == "ws":
            return None # WS tokens shouldn't be used for standard auth
    except (JWTError, KeyError, ValueError):
        return None
    user = user_repo.get(db, id=user_id)
    if not user or payload.get("token_version", 0) != user.token_version:
        return None
    return user


def create_ws_ticket(user_id: str) -> str:
    """Create a short-lived token specifically for WebSocket authentication."""
    expire = datetime.now(UTC) + timedelta(seconds=30)
    to_encode = {"sub": user_id, "type": "ws", "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_from_ws_ticket(ticket: str, db: Session) -> User | None:
    try:
        payload = jwt.decode(ticket, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "ws":
            return None
        user_id = uuid.UUID(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None
    return user_repo.get(db, id=user_id)
