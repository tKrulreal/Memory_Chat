"""
Connection API — Endpoints cho Connection Agent.

TASK-COP-04: Connection Agent + API
"""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.core.security import get_current_user
from src.models.contact import Contact
from src.models.user import User
from src.repositories.contact import ContactRepository

router = APIRouter()

CurrentUserDep = Annotated[User, Depends(get_current_user)]
DatabaseDep = Annotated[Session, Depends(get_db)]


# =============================================================================
# Schemas
# =============================================================================

class ConnectionPairResponse(BaseModel):
    contact_a_id: uuid.UUID
    contact_a_name: str
    contact_b_id: uuid.UUID
    contact_b_name: str
    score: float
    reason: str
    connection_type: str

    model_config = {"from_attributes": True}


class ConnectionListResponse(BaseModel):
    connections: list[ConnectionPairResponse]


class ConnectionStatusUpdate(BaseModel):
    status: str  # ACCEPTED, REJECTED, DISMISSED


# =============================================================================
# Helpers
# =============================================================================

def _verify_contact_access(db: Session, user_id: uuid.UUID, contact_id: uuid.UUID) -> Contact:
    """Verify user owns the contact."""
    repo = ContactRepository()
    from src.services.contact import ContactNotFoundError, ContactOwnershipError
    try:
        return repo.get_owned_contact(db, user_id, contact_id)
    except (ContactNotFoundError, ContactOwnershipError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found or access denied",
        ) from None


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/suggested", response_model=ConnectionListResponse)
async def get_suggested_connections(
    current_user: CurrentUserDep,
    db: DatabaseDep,
    limit: int = 5,
) -> ConnectionListResponse:
    """
    Lấy danh sách các cặp contacts có thể kết nối.

    Gọi ConnectionAgent để phân tích và đề xuất.
    """
    from src.agents.connection import ConnectionAgent

    agent = ConnectionAgent()
    pairs = await agent.find_connections(current_user.id, db, top_k=limit)

    return ConnectionListResponse(
        connections=[
            ConnectionPairResponse(
                contact_a_id=p.contact_a_id,
                contact_a_name=p.contact_a_name,
                contact_b_id=p.contact_b_id,
                contact_b_name=p.contact_b_name,
                score=p.score,
                reason=p.reason,
                connection_type=p.connection_type,
            )
            for p in pairs
        ]
    )


@router.get("/contact/{contact_id}", response_model=ConnectionListResponse)
async def get_connections_for_contact(
    contact_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    limit: int = 3,
) -> ConnectionListResponse:
    """
    Lấy danh sách connections cho một contact cụ thể.
    """
    # Verify access
    _verify_contact_access(db, current_user.id, contact_id)

    from src.agents.connection import ConnectionAgent

    agent = ConnectionAgent()
    pairs = agent.suggest_connections_for_contact(contact_id, db, top_k=limit)

    return ConnectionListResponse(
        connections=[
            ConnectionPairResponse(
                contact_a_id=p.contact_a_id,
                contact_a_name=p.contact_a_name,
                contact_b_id=p.contact_b_id,
                contact_b_name=p.contact_b_name,
                score=p.score,
                reason=p.reason,
                connection_type=p.connection_type,
            )
            for p in pairs
        ]
    )


@router.post("/accept/{pair_hash}")
async def accept_connection_suggestion(
    pair_hash: str,
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> dict[str, Any]:
    """
    User accept connection suggestion.

    pair_hash is a simple identifier (in production would be a stored pair ID).
    This endpoint logs the acceptance - actual connection management
    would be handled by the frontend.
    """
    # In MVP, we just acknowledge the acceptance
    # In full version, would store accepted pairs and potentially
    # send notifications or create connection records

    return {
        "status": "accepted",
        "pair_hash": pair_hash,
        "message": "Connection suggestion accepted. You can now introduce these contacts.",
    }


@router.post("/dismiss/{pair_hash}")
async def dismiss_connection_suggestion(
    pair_hash: str,
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> dict[str, Any]:
    """
    User dismiss connection suggestion.
    """
    return {
        "status": "dismissed",
        "pair_hash": pair_hash,
        "message": "Connection suggestion dismissed.",
    }
