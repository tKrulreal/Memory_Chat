import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SettingBase(BaseModel):
    theme: str = "system"
    language: str = "vi"
    notifications_enabled: bool = True
    sound_enabled: bool = True
    enter_is_send: bool = True
    read_receipts: bool = True
    online_status: bool = True
    media_auto_download: bool = True
    message_preview: bool = True
    accent_color: str = "blue"
    font_size: str = "medium"
    ai_enabled: bool = True
    ai_read_profile: bool = True
    ai_extract_chat: bool = True
    ai_memory_refresh_interval: str = "realtime"
    ai_memory_window: str = "unlimited"
    ai_recommendation_interval: str = "24h"
    ai_copilot_context_turns: int = 10


class SettingUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    notification: Optional[bool] = None
    sound_enabled: Optional[bool] = None
    enter_is_send: Optional[bool] = None
    read_receipts: Optional[bool] = None
    online_status: Optional[bool] = None
    media_auto_download: Optional[bool] = None
    message_preview: Optional[bool] = None
    accent_color: Optional[str] = None
    font_size: Optional[str] = None
    ai_enabled: Optional[bool] = None
    ai_read_profile: Optional[bool] = None
    ai_extract_chat: Optional[bool] = None
    ai_memory_refresh_interval: Optional[str] = None
    ai_memory_window: Optional[str] = None
    ai_recommendation_interval: Optional[str] = None
    ai_copilot_context_turns: Optional[int] = None


class SettingResponse(SettingBase):
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
