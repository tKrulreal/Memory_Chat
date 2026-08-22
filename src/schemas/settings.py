import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict

class SettingBase(BaseModel):
    theme: str = "light"
    notifications_enabled: bool = True
    ai_enabled: bool = True
    ai_read_profile: bool = True
    ai_memory_refresh_interval: str = "realtime"
    ai_memory_window: str = "unlimited"

class SettingUpdate(BaseModel):
    theme: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    ai_enabled: Optional[bool] = None
    ai_read_profile: Optional[bool] = None
    ai_memory_refresh_interval: Optional[str] = None
    ai_memory_window: Optional[str] = None

class SettingResponse(SettingBase):
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
