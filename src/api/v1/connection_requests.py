import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

from src.api.deps import get_db, get_event_bus
from src.core.security import get_current_user
from src.events.bus import EventBus
from src.events.types import EventType
from src.models.user import User
from src.models.connection import ConnectionRequest
from src.models.chat import Conversation
from src.schemas.connection import ConnectionRequestCreate, ConnectionRequestResponse
from src.schemas.pagination import PaginatedResponse, Pagination

router = APIRouter(prefix="/connection-requests", tags=["connection_requests"])

CurrentUserDep = Annotated[User, Depends(get_current_user)]
DatabaseDep = Annotated[Session, Depends(get_db)]
EventBusDep = Annotated[EventBus, Depends(get_event_bus)]

# ---------------------------------------------------------------------------
# Relationship resolver — single source of truth
# ---------------------------------------------------------------------------

UserRelation = Literal["none", "pending_sent", "pending_received", "friend"]


def get_relationship(
    db: Session,
    current_user_id: uuid.UUID,
    target_user_id: uuid.UUID,
) -> tuple[UserRelation, uuid.UUID | None]:
    """Return (relation, conversation_id).

    Resolution order:
    1. ACCEPTED connection   → friend
    2. Pending sent by me    → pending_sent
    3. Pending sent by them  → pending_received
    4. Otherwise             → none
    """
    # 1. Check accepted connection (means a direct conversation exists)
    existing_conv = (
        db.query(Conversation)
        .filter(
            or_(
                and_(
                    Conversation.user_a_id == current_user_id,
                    Conversation.user_b_id == target_user_id,
                ),
                and_(
                    Conversation.user_a_id == target_user_id,
                    Conversation.user_b_id == current_user_id,
                ),
            )
        )
        .first()
    )
    if existing_conv:
        return "friend", existing_conv.id

    # 2 & 3. Check pending request in either direction
    pending_req = (
        db.query(ConnectionRequest)
        .filter(
            or_(
                and_(
                    ConnectionRequest.sender_id == current_user_id,
                    ConnectionRequest.receiver_id == target_user_id,
                ),
                and_(
                    ConnectionRequest.sender_id == target_user_id,
                    ConnectionRequest.receiver_id == current_user_id,
                ),
            ),
            ConnectionRequest.status == "PENDING",
        )
        .first()
    )

    if pending_req:
        if pending_req.sender_id == current_user_id:
            return "pending_sent", None
        else:
            return "pending_received", None

    return "none", None


# ---------------------------------------------------------------------------
# Conversation helper
# ---------------------------------------------------------------------------

def _find_or_create_conversation(
    db: Session,
    user_id_a: uuid.UUID,
    user_id_b: uuid.UUID,
) -> Conversation:
    """Return existing direct conversation or create one.

    Enforces user_a_id < user_b_id to satisfy the chk_user_order constraint.
    """
    uid_a, uid_b = sorted([str(user_id_a), str(user_id_b)])
    existing = (
        db.query(Conversation)
        .filter(
            Conversation.user_a_id == uid_a,
            Conversation.user_b_id == uid_b,
        )
        .first()
    )
    if existing:
        return existing
    conv = Conversation(user_a_id=uid_a, user_b_id=uid_b)
    db.add(conv)
    db.flush()
    return conv


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("", response_model=PaginatedResponse[ConnectionRequestResponse])
def list_connection_requests(
    current_user: CurrentUserDep,
    db: DatabaseDep,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    direction: str = Query(default="all", description="all, incoming, outgoing"),
    status_filter: str = Query(default="PENDING", alias="status")
):
    query = db.query(ConnectionRequest).options(joinedload(ConnectionRequest.sender), joinedload(ConnectionRequest.receiver))

    if direction == "incoming":
        query = query.filter(ConnectionRequest.receiver_id == current_user.id)
    elif direction == "outgoing":
        query = query.filter(ConnectionRequest.sender_id == current_user.id)
    else:
        query = query.filter(
            or_(
                ConnectionRequest.sender_id == current_user.id,
                ConnectionRequest.receiver_id == current_user.id,
            )
        )

    if status_filter != "ALL":
        query = query.filter(ConnectionRequest.status == status_filter)

    total = query.count()
    requests = query.order_by(ConnectionRequest.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return PaginatedResponse(
        data=[ConnectionRequestResponse.model_validate(req) for req in requests],
        pagination=Pagination(page=page, limit=limit, total=total),
    )


@router.post("", response_model=ConnectionRequestResponse, status_code=status.HTTP_201_CREATED)
def send_connection_request(
    request_in: ConnectionRequestCreate,
    current_user: CurrentUserDep,
    db: DatabaseDep,
):
    # Resolve target user
    if not request_in.target_user_id and request_in.peer_email:
        peer = db.query(User).filter(User.email == request_in.peer_email).first()
        if not peer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        request_in.target_user_id = peer.id

    if not request_in.target_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide target_user_id or peer_email")

    if current_user.id == request_in.target_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot send request to yourself")

    target_user = db.get(User, request_in.target_user_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")

    # Resolve relationship — backend is the single source of truth
    relation, _ = get_relationship(db, current_user.id, target_user.id)

    if relation == "friend":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already connected",
        )
    if relation == "pending_sent":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Connection request already sent",
        )
    if relation == "pending_received":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user already sent you a request — accept it instead",
        )

    # Create new pending request
    new_req = ConnectionRequest(
        sender_id=current_user.id,
        receiver_id=target_user.id,
        status="PENDING",
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    return new_req


@router.post("/{request_id}/accept", response_model=ConnectionRequestResponse)
def accept_connection_request(
    request_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    event_bus: EventBusDep,
):
    req = db.get(ConnectionRequest, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection request not found")

    if req.receiver_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to accept this request")

    if req.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request is not pending")

    req.status = "ACCEPTED"

    # Find or create exactly one direct conversation (transactional, idempotent)
    conv = _find_or_create_conversation(db, req.sender_id, req.receiver_id)

    # Publish event so the UI can navigate to the conversation
    event_bus.publish(
        db=db,
        event_type=EventType.OPEN_CHAT,
        user_id=current_user.id,
        payload={"conversation_id": str(conv.id)},
        conversation_id=conv.id,
    )

    db.commit()
    db.refresh(req)
    return req


@router.post("/{request_id}/reject", response_model=ConnectionRequestResponse)
def reject_connection_request(
    request_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
):
    req = db.get(ConnectionRequest, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection request not found")

    if req.receiver_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to reject this request")

    if req.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request is not pending")

    req.status = "REJECTED"
    db.commit()
    db.refresh(req)
    return req


@router.post("/{request_id}/cancel", response_model=ConnectionRequestResponse)
def cancel_connection_request(
    request_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
):
    req = db.get(ConnectionRequest, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection request not found")

    if req.sender_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this request")

    if req.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request is not pending")

    req.status = "CANCELLED"
    db.commit()
    db.refresh(req)
    return req
