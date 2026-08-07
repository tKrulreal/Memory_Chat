"""
MemoryService — business logic cho ContactMemory.

Cung cấp methods để:
- Lấy memory theo contact
- Refresh memory (trigger Worker)
- User edit memory
- Lấy timeline từ ChromaDB
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from sqlalchemy.orm import Session

from src.events.bus import EventBus
from src.events.types import EventType
from src.models.contact import ContactMemory
from src.repositories.memory import MemoryRepository
from src.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

memory_repo = MemoryRepository(ContactMemory)


class MemoryService:
    """Service cho ContactMemory operations."""

    @staticmethod
    def get_by_contact(db: Session, contact_id: uuid.UUID) -> ContactMemory | None:
        """Lấy memory của một contact."""
        return db.query(ContactMemory).filter(
            ContactMemory.contact_id == contact_id
        ).first()

    @staticmethod
    def get_timeline(db: Session, contact_id: uuid.UUID, top_k: int = 20) -> list[dict[str, Any]]:
        """
        Lấy timeline events cho contact từ ChromaDB.

        Returns:
            List of {date, message_count, last_message_preview, participants}
        """
        vs = VectorStoreService.get_instance()
        try:
            results = vs.get_by_contact(str(contact_id), top_k=top_k)
            # ChromaDB doesn't store timeline, so we get from DB instead
            # Return empty list here — timeline comes from Conversation/Message history
            return []
        except Exception as e:
            logger.warning("Failed to get timeline from ChromaDB for contact %s: %s", contact_id, e)
            return []

    @staticmethod
    async def refresh(
        db: Session,
        event_bus: EventBus,
        contact_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Trigger memory refresh cho contact — emit OPEN_AI event → Worker xử lý.

        Args:
            db: Database session
            event_bus: EventBus instance
            contact_id: UUID của contact

        Returns:
            {"status": "triggered", "contact_id": str}
        """
        await event_bus.publish(
            EventType.OPEN_AI,
            user_id=uuid.uuid4(),  # Will be set by caller if needed
            payload={"contact_id": str(contact_id)},
            conversation_id=None,
        )
        logger.info("Memory refresh triggered for contact_id=%s", contact_id)
        return {"status": "triggered", "contact_id": str(contact_id)}

    @staticmethod
    def update(
        db: Session,
        contact_id: uuid.UUID,
        updates: dict[str, Any],
    ) -> ContactMemory:
        """
        User edit memory (summary, skills, interests, tags...).

        Args:
            db: Database session
            contact_id: UUID của contact
            updates: Dict chứa các fields cần update

        Returns:
            Updated ContactMemory
        """
        memory = db.query(ContactMemory).filter(
            ContactMemory.contact_id == contact_id
        ).first()

        if not memory:
            # Create new
            memory = ContactMemory(
                contact_id=contact_id,
                summary=updates.get("summary"),
                profession=updates.get("profession"),
                company=updates.get("company"),
                skills=updates.get("skills"),
                interest=updates.get("interest"),
                timeline=updates.get("timeline"),
                relationship_score=updates.get("relationship_score", 50),
            )
            db.add(memory)
            logger.info("Created new ContactMemory for contact_id=%s via user edit", contact_id)
        else:
            # Update existing
            allowed_fields = {
                "summary", "profession", "company", "skills",
                "interest", "timeline", "relationship_score",
            }
            for key, value in updates.items():
                if key in allowed_fields and value is not None:
                    setattr(memory, key, value)
            logger.info("Updated ContactMemory for contact_id=%s via user edit", contact_id)

        db.commit()
        db.refresh(memory)
        return memory

    @staticmethod
    def delete(db: Session, contact_id: uuid.UUID) -> bool:
        """Xoá memory của contact."""
        memory = db.query(ContactMemory).filter(
            ContactMemory.contact_id == contact_id
        ).first()
        if memory:
            db.delete(memory)
            db.commit()
            logger.info("Deleted ContactMemory for contact_id=%s", contact_id)
            return True
        return False
