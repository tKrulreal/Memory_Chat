from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.core.security import get_current_user
from src.models.user import User, Setting
from src.schemas.settings import SettingResponse, SettingUpdate

router = APIRouter()

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
    for key, value in update_data.items():
        setattr(setting, key, value)
        
    db.commit()
    db.refresh(setting)
    return setting
