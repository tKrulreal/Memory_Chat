from typing import Optional
from sqlalchemy.orm import Session
from src.repositories.base import BaseRepository
from src.models.contact import ContactMemory

class MemoryRepository(BaseRepository[ContactMemory]):
    def get_by_contact(self, db: Session, contact_id: str) -> Optional[ContactMemory]:
        return db.query(self.model).filter(self.model.contact_id == contact_id).first()

memory_repo = MemoryRepository(ContactMemory)
