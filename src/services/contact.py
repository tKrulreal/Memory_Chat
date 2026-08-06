import uuid

from sqlalchemy.orm import Session

from src.models.contact import Contact, ContactMemory
from src.repositories.contact import ContactRepository
from src.schemas.contact import ContactCreate, ContactResponse, ContactUpdate


class ContactNotFoundError(Exception):
    pass


class ContactOwnershipError(Exception):
    pass


class ContactService:
    def __init__(self, repository: ContactRepository):
        self.repository = repository

    def get_user_contacts(
        self,
        db: Session,
        user_id: uuid.UUID,
        page: int,
        limit: int,
        search: str | None = None,
    ) -> tuple[list[Contact], int]:
        skip = (page - 1) * limit
        contacts = self.repository.get_by_user_id(db, user_id, skip, limit, search)
        total = self.repository.count_by_user_id(db, user_id, search)
        return contacts, total

    def create_contact(self, db: Session, user_id: uuid.UUID, data: ContactCreate) -> Contact:
        values = data.model_dump(exclude_unset=True)
        relationship_score = values.pop("relationship_score", None)
        contact = self.repository.create(
            db,
            obj_in={
                "user_id": user_id,
                "display_name": values["name"],
                "avatar": values.get("avatar_url"),
            },
        )
        if relationship_score is not None:
            self._set_relationship_score(db, contact, relationship_score)
        return contact

    def get_owned_contact(self, db: Session, user_id: uuid.UUID, contact_id: uuid.UUID) -> Contact:
        contact = self.repository.get(db, id=contact_id)
        if contact is None:
            raise ContactNotFoundError
        if contact.user_id != user_id:
            raise ContactOwnershipError
        return contact

    def update_contact(
        self,
        db: Session,
        user_id: uuid.UUID,
        contact_id: uuid.UUID,
        data: ContactUpdate,
    ) -> Contact:
        contact = self.get_owned_contact(db, user_id, contact_id)
        values = data.model_dump(exclude_unset=True)
        relationship_score = values.pop("relationship_score", None)
        updates = {}
        if "name" in values:
            updates["display_name"] = values["name"]
        if "avatar_url" in values:
            updates["avatar"] = values["avatar_url"]
        if updates:
            contact = self.repository.update(db, contact, updates)
        if relationship_score is not None:
            self._set_relationship_score(db, contact, relationship_score)
        return contact

    def delete_contact(self, db: Session, user_id: uuid.UUID, contact_id: uuid.UUID) -> None:
        self.get_owned_contact(db, user_id, contact_id)
        self.repository.delete(db, contact_id)

    @staticmethod
    def to_response(contact: Contact) -> ContactResponse:
        response = ContactResponse.model_validate(contact)
        relationship_score = contact.memory.relationship_score if contact.memory else 0
        return response.model_copy(update={"relationship_score": relationship_score})

    @staticmethod
    def _set_relationship_score(db: Session, contact: Contact, relationship_score: int) -> None:
        memory = contact.memory
        if memory is None:
            memory = ContactMemory(contact_id=contact.id, relationship_score=relationship_score)
            db.add(memory)
        else:
            memory.relationship_score = relationship_score
        db.commit()
        db.refresh(contact)
