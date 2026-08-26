import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None = None
    
    model_config = ConfigDict(from_attributes=True)

class ConnectionRequestBase(BaseModel):
    pass

class ConnectionRequestCreate(ConnectionRequestBase):
    target_user_id: uuid.UUID | None = None
    peer_email: str | None = None

class ConnectionRequestUpdate(ConnectionRequestBase):
    status: str

class ConnectionRequestResponse(ConnectionRequestBase):
    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    sender: UserResponse
    receiver: UserResponse

    model_config = ConfigDict(from_attributes=True)
