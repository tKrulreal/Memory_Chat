import uuid
from typing import Annotated

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
    if not request_in.target_user_id and request_in.peer_email:
        peer = db.query(User).filter(User.email == request_in.peer_email).first()
        if not peer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        request_in.target_user_id = peer.id

    if not request_in.target_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide target_user_id or peer_email")

    if current_user.id == request_in.target_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot send request to yourself")

    # Check if target user exists
    target_user = db.get(User, request_in.target_user_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")

    # Check if a conversation already exists
    existing_conv = db.query(Conversation).filter(
        or_(
            and_(Conversation.user_a_id == current_user.id, Conversation.user_b_id == target_user.id),
            and_(Conversation.user_a_id == target_user.id, Conversation.user_b_id == current_user.id),
        )
    ).first()

    if existing_conv:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already connected")

    # Check existing connection request
    existing_req = db.query(ConnectionRequest).filter(
        or_(
            and_(ConnectionRequest.sender_id == current_user.id, ConnectionRequest.receiver_id == target_user.id),
            and_(ConnectionRequest.sender_id == target_user.id, ConnectionRequest.receiver_id == current_user.id),
        ),
        ConnectionRequest.status == "PENDING"
    ).first()

    if existing_req:
        if existing_req.sender_id == current_user.id:
            return existing_req
        else:
            # Mutual request intent: The other person already sent a request, so we auto-accept it.
            # However, for simplicity here, we can either return an error or accept it.
            # The prompt says: "treat this as mutual intent and avoid creating duplicate requests/conversations."
            existing_req.status = "ACCEPTED"
            
            # Create conversation
            new_conv = Conversation(user_a_id=existing_req.sender_id, user_b_id=existing_req.receiver_id)
            db.add(new_conv)
            db.commit()
            db.refresh(existing_req)
            return existing_req

    new_req = ConnectionRequest(
        sender_id=current_user.id,
        receiver_id=target_user.id,
        status="PENDING"
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
    
    # Check if conversation already exists just in case
    existing_conv = db.query(Conversation).filter(
        or_(
            and_(Conversation.user_a_id == req.sender_id, Conversation.user_b_id == req.receiver_id),
            and_(Conversation.user_a_id == req.receiver_id, Conversation.user_b_id == req.sender_id),
        )
    ).first()

    if not existing_conv:
        new_conv = Conversation(user_a_id=req.sender_id, user_b_id=req.receiver_id)
        db.add(new_conv)
        db.flush()
        
        # Publish event
        event_bus.publish(
            db=db,
            event_type=EventType.OPEN_CHAT,
            user_id=current_user.id,
            payload={"conversation_id": str(new_conv.id)},
            conversation_id=new_conv.id,
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
