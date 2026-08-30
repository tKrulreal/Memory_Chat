import uuid

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.core.rate_limit import limiter
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

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    return AuthService.register(db, user_in)

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    return AuthService.login(db, user_in)

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AuthService.change_password(db, current_user, req.current_password, req.new_password)


@router.post("/forgot-password")
@limiter.limit("5/hour")
def forgot_password(request: Request, req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    AuthService.request_password_reset(db, req.email)
    return {"message": "Nếu email tồn tại, chúng tôi đã gửi hướng dẫn đặt lại mật khẩu."}


@router.post("/reset-password")
@limiter.limit("5/hour")
def reset_password(request: Request, req: ResetPasswordRequest, db: Session = Depends(get_db)):
    return AuthService.reset_password(db, req.token, req.new_password)

class WSTicketResponse(BaseModel):
    ticket: str

@router.post("/ws-ticket", response_model=WSTicketResponse)
def get_ws_ticket(current_user: User = Depends(get_current_user)):
    from src.core.security import create_ws_ticket
    ticket = create_ws_ticket(str(current_user.id))
    return WSTicketResponse(ticket=ticket)
