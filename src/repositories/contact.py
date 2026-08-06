import uuid

from sqlalchemy.orm import Session

from src.models.contact import Contact
from src.repositories.base import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    def __init__(self):
        super().__init__(Contact)

    def get_by_user_id(
        self,
        db: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> list[Contact]:
        query = db.query(self.model).filter(Contact.user_id == user_id)
        if search:
            query = query.filter(Contact.display_name.ilike(f"%{search}%"))
        return query.order_by(Contact.display_name).offset(skip).limit(limit).all()

    def count_by_user_id(self, db: Session, user_id: uuid.UUID, search: str | None = None) -> int:
        query = db.query(self.model).filter(Contact.user_id == user_id)
        if search:
            query = query.filter(Contact.display_name.ilike(f"%{search}%"))
        return query.count()


contact_repo = ContactRepository()
