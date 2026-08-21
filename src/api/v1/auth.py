import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.core.security import get_current_user
from src.models.user import User
from src.services.auth import AuthService, UserCreate, UserLogin

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    gender: str | None = None
    phone: str | None = None

    model_config = ConfigDict(from_attributes=True)

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    return AuthService.register(db, user_in)

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    return AuthService.login(db, user_in)

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

class WSTicketResponse(BaseModel):
    ticket: str

@router.post("/ws-ticket", response_model=WSTicketResponse)
def get_ws_ticket(current_user: User = Depends(get_current_user)):
    from src.core.security import create_ws_ticket
    ticket = create_ws_ticket(str(current_user.id))
    return WSTicketResponse(ticket=ticket)
