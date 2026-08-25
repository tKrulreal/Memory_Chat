from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.security import create_access_token, get_password_hash, verify_password
from src.models.user import User
from src.repositories.user import user_repo


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    gender: str | None = None
    phone: str | None = None

class UserLogin(BaseModel):
    email: str
    password: str

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
        user = user_repo.get_by_email(db, email=data.email)
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

        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
