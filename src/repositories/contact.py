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

    def get_owned_contact(
        self,
        db: Session,
        user_id: uuid.UUID,
        contact_id: uuid.UUID,
    ) -> Contact:
        """
        Get a contact and verify ownership.

        Raises:
            ContactService.ContactNotFoundError: if contact does not exist
            ContactService.ContactOwnershipError: if user does not own the contact
        """
        # Import here to avoid circular dependency (services.contact uses repository)
        from src.services.contact import (
            ContactNotFoundError,
            ContactOwnershipError,
        )

        contact = self.get(db, id=contact_id)
        if contact is None:
            raise ContactNotFoundError(f"Contact {contact_id} not found")
        if contact.user_id != user_id:
            raise ContactOwnershipError(
                f"User {user_id} does not own contact {contact_id}"
            )
        return contact


contact_repo = ContactRepository()
