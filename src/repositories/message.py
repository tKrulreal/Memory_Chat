from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.chat import Message
from src.repositories.base import BaseRepository

class MessageRepository(BaseRepository[Message]):
    def __init__(self):
        super().__init__(Message)
        
    def get_by_conversation_id(self, db: Session, conversation_id: str, skip: int = 0, limit: int = 100) -> List[Message]:
        return db.query(self.model).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).offset(skip).limit(limit).all()

message_repo = MessageRepository()
