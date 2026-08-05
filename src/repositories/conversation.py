from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.chat import Conversation
from src.repositories.base import BaseRepository

class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self):
        super().__init__(Conversation)
        
    def get_by_user_id(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Conversation]:
        return db.query(self.model).filter(Conversation.user_id == user_id).offset(skip).limit(limit).all()

conversation_repo = ConversationRepository()
