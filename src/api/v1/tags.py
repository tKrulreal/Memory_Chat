import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.api.deps import get_db
from src.core.security import get_current_user
from src.models.user import User
from src.models.tag import Tag, UserTag, AISystemConfig
from src.schemas.tag import TagResponse, TagCreate, AISystemConfigResponse, AISystemConfigUpdate

router = APIRouter()

def get_admin_user(current_user: User = Depends(get_current_user)):
    # Simple placeholder for admin check based on email domain or a specific email
    # In a real app, this should check a role or is_superuser flag
    if not current_user.email.endswith("@admin.com"):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.get("/tags", response_model=list[TagResponse])
def get_system_tags(db: Session = Depends(get_db)):
    return db.query(Tag).filter(Tag.is_active == True).all()

@router.post("/tags", response_model=TagResponse)
def create_system_tag(
    req: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    normalized_name = " ".join([word.capitalize() for word in req.name.strip().split()])
    
    # Check if exists
    existing = db.query(Tag).filter(Tag.name.ilike(normalized_name)).first()
    if existing:
        if not existing.is_active:
            existing.is_active = True
            db.commit()
            db.refresh(existing)
            return existing
        return existing
        
    tag = Tag(name=normalized_name, category=req.category, is_active=req.is_active)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@router.delete("/tags/{tag_id}")
def delete_system_tag(
    tag_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    tag.is_active = False
    db.commit()
    return {"status": "success"}

@router.get("/users/me/tags", response_model=list[TagResponse])
def get_my_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_tags = db.query(UserTag).filter(UserTag.user_id == current_user.id).all()
    if not user_tags:
        return []
    tag_ids = [ut.tag_id for ut in user_tags]
    tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
    return tags

class AddTagRequest(BaseModel):
    tag_id: uuid.UUID

@router.post("/users/me/tags")
def add_my_tag(
    req: AddTagRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tag = db.query(Tag).filter(Tag.id == req.tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
        
    existing = db.query(UserTag).filter(
        UserTag.user_id == current_user.id,
        UserTag.tag_id == req.tag_id
    ).first()
    if not existing:
        user_tag = UserTag(user_id=current_user.id, tag_id=req.tag_id)
        db.add(user_tag)
        db.commit()
    return {"status": "success"}

@router.delete("/users/me/tags/{tag_id}")
def remove_my_tag(
    tag_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_tag = db.query(UserTag).filter(
        UserTag.user_id == current_user.id,
        UserTag.tag_id == tag_id
    ).first()
    if user_tag:
        db.delete(user_tag)
        db.commit()
    return {"status": "success"}
    
# AI System Config endpoints
@router.get("/ai-config", response_model=list[AISystemConfigResponse])
def get_ai_configs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    configs = db.query(AISystemConfig).filter(AISystemConfig.user_id == current_user.id).all()
    if not configs:
        default_config = AISystemConfig(
            user_id=current_user.id,
            key="system_prompt",
            value={"role": "system", "content": "You are a helpful AI Matchmaker agent. Analyze user chats to find common interests and propose connections."},
            description="System rules for AI Matchmaker"
        )
        db.add(default_config)
        db.commit()
        db.refresh(default_config)
        configs.append(default_config)
    return configs

@router.patch("/ai-config/{key}", response_model=AISystemConfigResponse)
def update_ai_config(
    key: str,
    req: AISystemConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    config = db.query(AISystemConfig).filter(
        AISystemConfig.user_id == current_user.id,
        AISystemConfig.key == key
    ).first()
    
    if not config:
        config = AISystemConfig(
            user_id=current_user.id,
            key=key,
            value=req.value,
            description=req.description
        )
        db.add(config)
    else:
        config.value = req.value
        if req.description:
            config.description = req.description
    db.commit()
    db.refresh(config)
    return config
