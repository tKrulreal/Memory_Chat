import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict

class SettingBase(BaseModel):
    theme: str = "light"
    notifications_enabled: bool = True
    ai_enabled: bool = True
    ai_memory_window: int = 10

class SettingUpdate(BaseModel):
    theme: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    ai_enabled: Optional[bool] = None
    ai_memory_window: Optional[int] = None

class SettingResponse(SettingBase):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
