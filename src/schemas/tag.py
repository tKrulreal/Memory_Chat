import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TagBase(BaseModel):
    name: str
    category: Optional[str] = None
    is_active: bool = True

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class TagResponse(TagBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class AISystemConfigBase(BaseModel):
    key: str
    value: dict
    description: Optional[str] = None

class AISystemConfigUpdate(BaseModel):
    value: dict
    description: Optional[str] = None

class AISystemConfigResponse(AISystemConfigBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
