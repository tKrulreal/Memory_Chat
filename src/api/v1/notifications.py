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

from typing import Any

class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    type: str
    title: str
    content: str
    status: str
    data: dict[str, Any] | None = None
    created_at: str

    model_config = {"from_attributes": True}

def _get_user_recommendation_settings(db: Session, current_user: User) -> tuple[bool, int]:
    from src.models.tag import AISystemConfig
    ai_config = db.query(AISystemConfig).filter(
        AISystemConfig.user_id == current_user.id,
        AISystemConfig.key == "ai_settings"
    ).first()

    recommendation_enabled = True
    raw_score = 50

    if not current_user.setting or not current_user.setting.ai_enabled:
        recommendation_enabled = False

    if ai_config and isinstance(ai_config.value, dict):
        features = ai_config.value.get("features", {})
        if features.get("recommendation") is False:
            recommendation_enabled = False
        raw_score = ai_config.value.get("min_matching_score", 50)
    elif current_user.setting:
        raw_score = getattr(current_user.setting, "ai_matching_threshold", 50)

    try:
        val = float(raw_score)
        min_score_percent = int(round(val * 100)) if val <= 1.0 else int(round(val))
    except Exception:
        min_score_percent = 50

    return recommendation_enabled, min_score_percent


def _is_notification_visible(notif: Notification, recommendation_enabled: bool, min_score_percent: int) -> bool:
    matching_types = {"MATCH_SUGGESTION", "CONNECTION_RECOMMENDATION", "RECOMMENDATION"}
    if notif.type in matching_types:
        if not recommendation_enabled:
            return False
        n_data = notif.data or {}
        score = n_data.get("match_score")
        if score is not None:
            try:
                s_val = float(score)
                s_percent = int(round(s_val * 100)) if s_val <= 1.0 else int(round(s_val))
                if s_percent < min_score_percent:
                    return False
            except Exception:
                pass
    return True


@router.get("", response_model=PaginatedResponse[NotificationResponse])
def list_notifications(
    current_user: CurrentUserDep,
    db: DatabaseDep,
    type_filter: Annotated[str | None, Query(alias="type")] = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    skip = (page - 1) * limit
    recommendation_enabled, min_score_percent = _get_user_recommendation_settings(db, current_user)

    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if type_filter:
        query = query.filter(Notification.type == type_filter)
    if status_filter:
        query = query.filter(Notification.status == status_filter)

    all_notifications = query.order_by(Notification.created_at.desc()).all()
    visible_notifications = [
        n for n in all_notifications
        if _is_notification_visible(n, recommendation_enabled, min_score_percent)
    ]

    total = len(visible_notifications)
    notifications = visible_notifications[skip : skip + limit]

    data = []
    for notif in notifications:
        n_resp = NotificationResponse(
            id=notif.id,
            user_id=notif.user_id,
            type=notif.type,
            title=notif.title,
            content=notif.content,
            status=notif.status,
            data=notif.data or {},
            created_at=notif.created_at.isoformat() if notif.created_at else ""
        )
        data.append(n_resp)

    return PaginatedResponse(
        data=data,
        pagination=Pagination(page=page, limit=limit, total=total)
    )


@router.get("/unread-count")
def get_unread_count(
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> dict[str, int]:
    recommendation_enabled, min_score_percent = _get_user_recommendation_settings(db, current_user)
    unreads = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.status == "UNREAD"
    ).all()
    count = sum(1 for n in unreads if _is_notification_visible(n, recommendation_enabled, min_score_percent))
    return {"unread_count": count}


@router.post("/read-all")
def mark_all_notifications_read(
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> dict[str, Any]:
    updated = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.status == "UNREAD"
    ).update({"status": "READ"}, synchronize_session=False)
    db.commit()
    return {"status": "success", "marked_read": updated}


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
        data=notif.data or {},
        created_at=notif.created_at.isoformat() if notif.created_at else ""
    )


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> dict[str, Any]:
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    db.delete(notif)
    db.commit()
    return {"status": "success", "deleted_id": str(notification_id)}
