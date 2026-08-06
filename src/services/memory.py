from sqlalchemy.orm import Session
from src.repositories.memory import memory_repo
from src.models.contact import ContactMemory

class MemoryService:
    @staticmethod
    def get_by_contact(db: Session, contact_id: str):
        return memory_repo.get_by_contact(db, contact_id=contact_id)
    
    @staticmethod
    def create(db: Session, obj_in: dict):
        # Trigger memory agent logic could be placed here
        return memory_repo.create(db, obj_in=obj_in)
    
    @staticmethod
    def update(db: Session, db_obj: ContactMemory, obj_in: dict):
        return memory_repo.update(db, db_obj=db_obj, obj_in=obj_in)
