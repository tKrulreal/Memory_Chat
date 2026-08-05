from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.contact import Contact
from src.repositories.base import BaseRepository

class ContactRepository(BaseRepository[Contact]):
    def __init__(self):
        super().__init__(Contact)
        
    def get_by_user_id(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Contact]:
        return db.query(self.model).filter(Contact.user_id == user_id).offset(skip).limit(limit).all()
        
contact_repo = ContactRepository()
