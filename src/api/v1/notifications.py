import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.core.security import get_current_user
from src.models.user import Notification, User
from src.schemas.pagination import PaginatedResponse, Pagination

router = APIRouter()

CurrentUserDep = Annotated[User, Depends(get_current_user)]
DatabaseDep = Annotated[Session, Depends(get_db)]

class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    type: str
    title: str
    content: str
    status: str
    created_at: str

    model_config = {"from_attributes": True}

@router.get("", response_model=PaginatedResponse[NotificationResponse])
def list_notifications(
    current_user: CurrentUserDep,
    db: DatabaseDep,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    skip = (page - 1) * limit

    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    total = query.count()
    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    data = []
    for notif in notifications:
        n_resp = NotificationResponse(
            id=notif.id,
            user_id=notif.user_id,
            type=notif.type,
            title=notif.title,
            content=notif.content,
            status=notif.status,
            created_at=notif.created_at.isoformat() if notif.created_at else ""
        )
        data.append(n_resp)

    return PaginatedResponse(
        data=data,
        pagination=Pagination(page=page, limit=limit, total=total)
    )


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
):
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    if notif.status != "READ":
        notif.status = "READ"
        db.commit()
        db.refresh(notif)

    return NotificationResponse(
        id=notif.id,
        user_id=notif.user_id,
        type=notif.type,
        title=notif.title,
        content=notif.content,
        status=notif.status,
        created_at=notif.created_at.isoformat() if notif.created_at else ""
    )
