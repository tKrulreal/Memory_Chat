"""
Memory API — REST endpoints cho ContactMemory.

Endpoints:
- GET  /api/v1/memory/{contact_id}               — Lấy Memory hiện tại
- POST /api/v1/memory/{contact_id}/refresh       — Trigger refresh ngay
- PATCH /api/v1/memory/{contact_id}             — User edit Memory
- GET  /api/v1/memory/{contact_id}/timeline     — Lấy timeline
"""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_event_bus
from src.core.security import get_current_user
from src.models.user import User
from src.services.memory import MemoryService


router = APIRouter()

# Dependency aliases (same pattern as contacts.py)
CurrentUserDep = Annotated[User, Depends(get_current_user)]
DatabaseDep = Annotated[Session, Depends(get_db)]
EventBusDep = Annotated[Any, Depends(get_event_bus)]


# --- Request/Response Schemas ---

class MemoryTimelineResponse(BaseModel):
    date: str
    message_count: int
    last_message_preview: str
    participants: list[str]

    model_config = {"from_attributes": True}


class MemoryResponse(BaseModel):
    id: uuid.UUID
    contact_id: uuid.UUID
    summary: str | None = None
    profession: str | None = None
    company: str | None = None
    skills: dict | None = None
    interest: dict | None = None
    timeline: dict | None = None
    relationship_score: int | None = None
    last_discussion: str | None = None
    updated_at: str | None = None

    model_config = {"from_attributes": True}


class MemoryUpdateRequest(BaseModel):
    summary: str | None = Field(None, min_length=1)
    profession: str | None = Field(None, min_length=1)
    company: str | None = Field(None, min_length=1)
    skills: dict | None = None
    interest: dict | None = None
    relationship_score: int | None = Field(None, ge=0, le=100)

    model_config = {"extra": "forbid"}


class MemoryRefreshResponse(BaseModel):
    status: str
    contact_id: str


class MemoryErrorResponse(BaseModel):
    detail: str


# --- Endpoints ---


@router.get("/{contact_id}", response_model=MemoryResponse | None)
def get_contact_memory(
    contact_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> MemoryResponse | None:
    """
    Lấy Memory hiện tại của một Contact.

    Returns 404 nếu contact không có memory.
    """
    # Verify contact ownership
    from src.repositories.contact import ContactRepository
    from src.services.contact import ContactOwnershipError

    contact_repo = ContactRepository()
    try:
        contact = contact_repo.get_owned_contact(db, current_user.id, contact_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found or access denied",
        ) from None

    memory = MemoryService.get_by_contact(db, contact_id)
    if not memory:
        return None

    return MemoryResponse(
        id=memory.id,
        contact_id=memory.contact_id,
        summary=memory.summary,
        profession=memory.profession,
        company=memory.company,
        skills=memory.skills,
        interest=memory.interest,
        timeline=memory.timeline,
        relationship_score=memory.relationship_score,
        last_discussion=memory.last_discussion,
        updated_at=memory.updated_at.isoformat() if memory.updated_at else None,
    )


@router.post(
    "/{contact_id}/refresh",
    response_model=MemoryRefreshResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_memory_refresh(
    contact_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    event_bus: EventBusDep,
) -> MemoryRefreshResponse:
    """
    Trigger Memory Refresh ngay lập tức.

    Emit event OPEN_AI → Memory Worker xử lý async.
    """
    # Verify contact ownership
    from src.repositories.contact import ContactRepository

    contact_repo = ContactRepository()
    try:
        contact_repo.get_owned_contact(db, current_user.id, contact_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found or access denied",
        ) from None

    result = await MemoryService.refresh(db, event_bus, contact_id)
    return MemoryRefreshResponse(**result)


@router.patch("/{contact_id}", response_model=MemoryResponse)
def update_contact_memory(
    contact_id: uuid.UUID,
    updates: MemoryUpdateRequest,
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> MemoryResponse:
    """
    User edit Memory (summary, profession, skills, interests...).
    """
    # Verify contact ownership
    from src.repositories.contact import ContactRepository

    contact_repo = ContactRepository()
    try:
        contact_repo.get_owned_contact(db, current_user.id, contact_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found or access denied",
        ) from None

    updates_dict = updates.model_dump(exclude_unset=True)
    if not updates_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    memory = MemoryService.update(db, contact_id, updates_dict)

    return MemoryResponse(
        id=memory.id,
        contact_id=memory.contact_id,
        summary=memory.summary,
        profession=memory.profession,
        company=memory.company,
        skills=memory.skills,
        interest=memory.interest,
        timeline=memory.timeline,
        relationship_score=memory.relationship_score,
        last_discussion=memory.last_discussion,
        updated_at=memory.updated_at.isoformat() if memory.updated_at else None,
    )


@router.get("/{contact_id}/timeline", response_model=list[MemoryTimelineResponse])
def get_contact_memory_timeline(
    contact_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> list[MemoryTimelineResponse]:
    """
    Lấy timeline (sự kiện theo thời gian) cho một Contact.

    Timeline được build từ Message history trong DB.
    """
    # Verify contact ownership
    from src.repositories.contact import ContactRepository

    contact_repo = ContactRepository()
    try:
        contact_repo.get_owned_contact(db, current_user.id, contact_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found or access denied",
        ) from None

    # Build timeline from Message history
    from src.models.chat import Conversation, Message
    from sqlalchemy import func, cast, String

    # Group messages by date
    date_expr = func.date(Message.created_at).label("date")

    results = (
        db.query(
            date_expr,
            func.count(Message.id).label("message_count"),
            func.max(Message.content).label("last_message"),
        )
        .join(Conversation, Conversation.id == Message.conversation_id)
        .filter(Conversation.contact_id == contact_id)
        .group_by(date_expr)
        .order_by(date_expr.desc())
        .limit(20)
        .all()
    )

    timeline = [
        MemoryTimelineResponse(
            date=str(row.date) if row.date else "",
            message_count=row.message_count or 0,
            last_message_preview=(row.last_message or "")[:100],
            participants=["USER", "CONTACT"],
        )
        for row in results
    ]

    return timeline
