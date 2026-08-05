from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.repositories.conversation import conversation_repo
from src.models.chat import Conversation

class ConversationService:
    @staticmethod
    def get_user_conversations(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Conversation]:
        return conversation_repo.get_by_user_id(db, user_id=user_id, skip=skip, limit=limit)
        
    @staticmethod
    def create_conversation(db: Session, user_id: str, contact_id: str, title: Optional[str] = None) -> Conversation:
        obj_in = {
            "user_id": user_id,
            "contact_id": contact_id,
            "title": title
        }
        return conversation_repo.create(db, obj_in=obj_in)

    @staticmethod
    def get_conversation(db: Session, conversation_id: str) -> Optional[Conversation]:
        return conversation_repo.get(db, id=conversation_id)
