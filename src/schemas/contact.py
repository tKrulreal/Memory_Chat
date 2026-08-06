from typing import Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict

class ContactBase(BaseModel):
    name: str = Field(..., min_length=1, description="Tên liên hệ không được rỗng")
    avatar_url: Optional[str] = None
    relationship_score: Optional[int] = Field(0, description="Điểm mối quan hệ")

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    avatar_url: Optional[str] = None
    relationship_score: Optional[int] = None

class ContactResponse(ContactBase):
    id: uuid.UUID
    user_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)
