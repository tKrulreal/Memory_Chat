
from sqlalchemy.orm import Session

from src.models.contact import ContactMemory
from src.repositories.base import BaseRepository


class MemoryRepository(BaseRepository[ContactMemory]):
    def get_by_contact(self, db: Session, contact_id: str) -> ContactMemory | None:
        return db.query(self.model).filter(self.model.contact_id == contact_id).first()

memory_repo = MemoryRepository(ContactMemory)
