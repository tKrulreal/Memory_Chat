from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api.ws import manager
from src.core.security import get_current_user
from src.models.user import User

router = APIRouter()


class PresenceResponse(BaseModel):
    online_user_ids: list[str]


@router.get("/online", response_model=PresenceResponse)
def get_online_users(current_user: User = Depends(get_current_user)):
    return PresenceResponse(online_user_ids=manager.get_online_user_ids())
