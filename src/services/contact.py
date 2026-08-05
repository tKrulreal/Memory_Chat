from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.repositories.contact import contact_repo
from src.models.contact import Contact

class ContactService:
    @staticmethod
    def get_user_contacts(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Contact]:
        return contact_repo.get_by_user_id(db, user_id=user_id, skip=skip, limit=limit)
        
    @staticmethod
    def create_contact(db: Session, user_id: str, data: Dict[str, Any]) -> Contact:
        obj_in = data.copy()
        obj_in["user_id"] = user_id
        return contact_repo.create(db, obj_in=obj_in)

    @staticmethod
    def get_contact(db: Session, contact_id: str) -> Optional[Contact]:
        return contact_repo.get(db, id=contact_id)
        
    @staticmethod
    def update_contact(db: Session, contact_id: str, data: Dict[str, Any]) -> Optional[Contact]:
        contact = contact_repo.get(db, id=contact_id)
        if not contact:
            return None
        return contact_repo.update(db, db_obj=contact, obj_in=data)
