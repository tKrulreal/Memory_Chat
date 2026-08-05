from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.repositories.message import message_repo
from src.models.chat import Message

class MessageService:
    @staticmethod
    def get_conversation_messages(db: Session, conversation_id: str, skip: int = 0, limit: int = 100) -> List[Message]:
        return message_repo.get_by_conversation_id(db, conversation_id=conversation_id, skip=skip, limit=limit)
        
    @staticmethod
    def create_message(db: Session, conversation_id: str, sender_type: str, content: str, message_type: str = "TEXT") -> Message:
        obj_in = {
            "conversation_id": conversation_id,
            "sender_type": sender_type,
            "content": content,
            "message_type": message_type
        }
        return message_repo.create(db, obj_in=obj_in)
