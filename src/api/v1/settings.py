import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.core.security import get_current_user
from src.models.user import User, Setting, UserBlock
from src.schemas.settings import SettingResponse, SettingUpdate

router = APIRouter()


class BlockedUserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None = None
    avatar: str | None = None
    blocked_at: str


@router.get("/me/settings", response_model=SettingResponse)
def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    setting = db.query(Setting).filter(Setting.user_id == current_user.id).first()
    if not setting:
        # Create default setting if not exists
        setting = Setting(user_id=current_user.id)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting


@router.patch("/me/settings", response_model=SettingResponse)
def update_settings(
    req: SettingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    setting = db.query(Setting).filter(Setting.user_id == current_user.id).first()
    if not setting:
        setting = Setting(user_id=current_user.id)
        db.add(setting)
    
    update_data = req.model_dump(exclude_unset=True)
    if "notifications_enabled" in update_data:
        setting.notification = update_data["notifications_enabled"]
    if "notification" in update_data:
        setting.notification = update_data["notification"]

    for key, value in update_data.items():
        if hasattr(setting, key):
            setattr(setting, key, value)
        
    # Synchronize relevant settings to AISystemConfig (ai_settings)
    from src.models.tag import AISystemConfig
    ai_config = db.query(AISystemConfig).filter(
        AISystemConfig.user_id == current_user.id,
        AISystemConfig.key == "ai_settings"
    ).first()

    if ai_config and isinstance(ai_config.value, dict):
        new_val = dict(ai_config.value)
        updated_ai_cfg = False
        if "ai_matching_threshold" in update_data:
            new_val["min_matching_score"] = setting.ai_matching_threshold
            updated_ai_cfg = True
        if "ai_recommendation_interval" in update_data:
            new_val["notification_interval"] = setting.ai_recommendation_interval
            updated_ai_cfg = True
        if "ai_enabled" in update_data and "features" in new_val and isinstance(new_val["features"], dict):
            new_val["features"]["recommendation"] = setting.ai_enabled
            updated_ai_cfg = True

        if updated_ai_cfg:
            ai_config.value = new_val

    db.commit()
    db.refresh(setting)
    return setting


@router.get("/me/blocked-users", response_model=list[BlockedUserResponse])
def get_blocked_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách người dùng mà tôi đã chặn."""
    blocks = (
        db.query(UserBlock)
        .filter(UserBlock.blocker_id == current_user.id)
        .order_by(UserBlock.created_at.desc())
        .all()
    )
    result = []
    for b in blocks:
        target = db.get(User, b.blocked_id)
        if target:
            result.append(
                BlockedUserResponse(
                    id=target.id,
                    email=target.email,
                    full_name=target.full_name,
                    avatar=target.avatar,
                    blocked_at=b.created_at.isoformat() if b.created_at else "",
                )
            )
    return result


@router.post("/me/block/{target_user_id}")
def block_user(
    target_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chặn một người dùng."""
    if target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Bạn không thể tự chặn chính mình")

    target = db.get(User, target_user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    existing = (
        db.query(UserBlock)
        .filter(
            UserBlock.blocker_id == current_user.id,
            UserBlock.blocked_id == target_user_id,
        )
        .first()
    )
    if not existing:
        block = UserBlock(blocker_id=current_user.id, blocked_id=target_user_id)
        db.add(block)
        db.commit()

    return {"message": "Đã chặn người dùng thành công", "blocked_id": str(target_user_id)}


@router.delete("/me/unblock/{target_user_id}")
def unblock_user(
    target_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mở chặn một người dùng."""
    block = (
        db.query(UserBlock)
        .filter(
            UserBlock.blocker_id == current_user.id,
            UserBlock.blocked_id == target_user_id,
        )
        .first()
    )
    if block:
        db.delete(block)
        db.commit()

    return {"message": "Đã bỏ chặn người dùng", "unblocked_id": str(target_user_id)}
