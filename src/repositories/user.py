
from sqlalchemy.orm import Session

from src.models.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(self.model).filter(User.email == email).first()

user_repo = UserRepository()
