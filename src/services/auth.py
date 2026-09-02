import hashlib
import secrets
import smtplib
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.config import get_settings
from src.core.security import create_access_token, get_password_hash, verify_password
from src.models.user import PasswordResetToken, User
from src.repositories.user import user_repo
from src.services.email import send_password_reset_email


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    gender: str | None = None
    phone: str | None = None

class UserLogin(BaseModel):
    email: str
    password: str


def _hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

class AuthService:
    @staticmethod
    def register(db: Session, data: UserCreate) -> User:
        # Check if user exists
        existing_user = user_repo.get_by_email(db, email=data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        hashed_password = get_password_hash(data.password)
        obj_in = {
            "email": data.email,
            "password_hash": hashed_password,
            "full_name": data.full_name,
            "gender": data.gender,
            "phone": data.phone,
        }
        user = user_repo.create(db, obj_in=obj_in)
        return user

    @staticmethod
    def login(db: Session, data: UserLogin) -> dict[str, str]:
        user = user_repo.get_by_email_or_phone(db, identifier=data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Seamlessly upgrade legacy non-bcrypt password hashes
        if user.password_hash and not user.password_hash.startswith(("$2b$", "$2a$")):
            user.password_hash = get_password_hash(data.password)
            db.commit()

        access_token = create_access_token(data={"sub": str(user.id), "token_version": user.token_version})
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def change_password(db: Session, user: User, current_password: str, new_password: str) -> dict[str, str]:
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu hiện tại không chính xác",
            )
        if len(new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu mới phải có tối thiểu 6 ký tự",
            )
        user.password_hash = get_password_hash(new_password)
        user.token_version += 1
        db.commit()
        return {"message": "Đổi mật khẩu thành công"}

    @staticmethod
    def request_password_reset(db: Session, email: str) -> None:
        user = user_repo.get_by_email(db, email=email)
        if not user:
            return

        settings = get_settings()
        now = datetime.now(UTC)
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        ).update({PasswordResetToken.used_at: now}, synchronize_session=False)

        token = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=_hash_reset_token(token),
            expires_at=now + timedelta(minutes=settings.password_reset_token_minutes),
        )
        db.add(reset_token)
        db.commit()

        reset_url = f"{settings.frontend_url.rstrip('/')}/reset-password?token={token}"
        try:
            send_password_reset_email(user.email, reset_url)
        except (OSError, smtplib.SMTPException):
            return

    @staticmethod
    def reset_password_by_identity(
        db: Session,
        email: str,
        full_name: str,
        phone: str | None,
        new_password: str,
    ) -> dict[str, str]:
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu mới phải có tối thiểu 8 ký tự",
            )

        user = user_repo.get_for_password_reset(db, email=email, full_name=full_name)
        if not user or (user.phone and user.phone != phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thông tin xác minh không chính xác",
            )

        user.password_hash = get_password_hash(new_password)
        user.token_version += 1
        db.commit()
        return {"message": "Đặt lại mật khẩu thành công"}

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> dict[str, str]:
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu mới phải có tối thiểu 8 ký tự",
            )

        now = datetime.now(UTC)
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token_hash == _hash_reset_token(token),
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > now,
        ).first()
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn",
            )

        reset_token.user.password_hash = get_password_hash(new_password)
        reset_token.user.token_version += 1
        reset_token.used_at = now
        db.commit()
        return {"message": "Đặt lại mật khẩu thành công"}
