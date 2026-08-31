
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.models.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(self.model).filter(User.email == email).first()

    def get_by_email_or_phone(self, db: Session, identifier: str) -> User | None:
        return db.query(self.model).filter(
            or_(User.email == identifier, User.phone == identifier)
        ).first()

    def get_for_password_reset(
        self, db: Session, email: str, full_name: str
    ) -> User | None:
        return db.query(self.model).filter(
            User.email == email,
            User.full_name == full_name,
            User.deleted_at.is_(None),
        ).first()

user_repo = UserRepository()
