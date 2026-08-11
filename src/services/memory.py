"""
MemoryService — business logic cho ContactMemory.

Cung cấp methods để:
- Lấy memory theo contact
- Refresh memory (trigger Worker)
- User edit memory
"""

import logging
import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.events.bus import EventBus
from src.events.types import EventType
from src.models.contact import ContactMemory

logger = logging.getLogger(__name__)


class MemoryService:
    """Service cho ContactMemory operations."""

    @staticmethod
    def get_by_contact(db: Session, contact_id: uuid.UUID) -> ContactMemory | None:
        """Lấy memory của một contact."""
        return db.query(ContactMemory).filter(
            ContactMemory.contact_id == contact_id
        ).first()

    @staticmethod
    async def refresh(
        db: Session,
        event_bus: EventBus,
        contact_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        """
        Trigger memory refresh cho contact — emit OPEN_AI event → Worker xử lý.

        Args:
            db: Database session
            event_bus: EventBus instance
            contact_id: UUID của contact
            user_id: UUID của user đang trigger refresh (để tracking audit)

        Returns:
            {"status": "triggered", "contact_id": str}
        """
        # Use provided user_id, or fallback to N/A sentinel (4-zero UUID)
        # Most callers should pass user_id from the authenticated request
        effective_user_id = user_id if user_id is not None else uuid.UUID(int=0)

        await event_bus.publish(
            EventType.OPEN_AI,
            user_id=effective_user_id,
            payload={"contact_id": str(contact_id)},
            conversation_id=None,
        )
        logger.info(
            "Memory refresh triggered for contact_id=%s by user_id=%s",
            contact_id,
            effective_user_id,
        )
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
            # Update existing — only update fields with non-None values
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
