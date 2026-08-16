"""
User Profile API (v1).
Quản lý thông tin hồ sơ cá nhân do người dùng tự nhập để phục vụ tìm kiếm & so khớp gợi ý kết nối.
"""

from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.v1.auth import get_current_user

from src.models.user import User, UserProfile
from src.agents.connection.agent import ConnectionRecommendationAgent

router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    avatar: str | None = None
    profession: str | None = Field(default=None, description="Chuyên môn / Chức danh")
    company: str | None = Field(default=None, description="Công ty / Tổ chức công tác")
    location: str | None = Field(default=None, description="Địa điểm / Thành phố (Hà Nội, TP.HCM, ...)")
    skills: list[str] = Field(default_factory=list, description="Danh sách kỹ năng chuyên môn")
    interests: list[str] = Field(default_factory=list, description="Lĩnh vực quan tâm / Sở thích")
    looking_for: list[str] = Field(default_factory=list, description="Nhu cầu tìm kiếm (AI projects, đối tác, tuyển dụng...)")
    offering: list[str] = Field(default_factory=list, description="Thế mạnh có thể đóng góp/chia sẻ")
    bio: str | None = Field(default=None, description="Giới thiệu bản thân ngắn gọn")


class ProfileResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str | None
    avatar: str | None
    profession: str | None
    company: str | None
    location: str | None
    skills: list[str]
    interests: list[str]
    looking_for: list[str]
    offering: list[str]
    bio: str | None
    is_custom_profile: bool = Field(description="True nếu người dùng đã tự nhập thông tin vào bảng UserProfile")
    created_at: datetime | None = None
    updated_at: datetime | None = None


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy thông tin hồ sơ của người dùng hiện tại:
    - Nếu đã tự nhập trong UserProfile: Trả về thông tin do chính người dùng nhập.
    - Nếu chưa nhập: Trả về thông tin trích xuất tự động từ hội thoại chat thực tế.
    """
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    # Dùng Agent để lấy profile hợp nhất (UserProfile -> Chat extraction)
    agent = ConnectionRecommendationAgent()
    unified_dict = agent.extract_user_profile(current_user, db)

    is_custom = user_profile is not None and any([
        user_profile.profession,
        user_profile.company,
        user_profile.location,
        user_profile.skills,
        user_profile.interests,
        user_profile.looking_for,
        user_profile.offering,
        user_profile.bio,
    ])

    return ProfileResponse(
        user_id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name or unified_dict["full_name"],
        avatar=current_user.avatar,
        profession=user_profile.profession if (user_profile and user_profile.profession) else unified_dict.get("profession"),
        company=user_profile.company if (user_profile and user_profile.company) else unified_dict.get("company"),
        location=user_profile.location if (user_profile and user_profile.location) else unified_dict.get("location"),
        skills=user_profile.skills if (user_profile and user_profile.skills) else unified_dict.get("skills", []),
        interests=user_profile.interests if (user_profile and user_profile.interests) else unified_dict.get("interests", []),
        looking_for=user_profile.looking_for if (user_profile and user_profile.looking_for) else unified_dict.get("current_needs", []),
        offering=user_profile.offering if (user_profile and user_profile.offering) else unified_dict.get("current_offers", []),
        bio=user_profile.bio if user_profile else None,
        is_custom_profile=is_custom,
        created_at=user_profile.created_at if user_profile else current_user.created_at,
        updated_at=user_profile.updated_at if user_profile else current_user.updated_at,
    )


@router.put("/me", response_model=ProfileResponse)
def update_my_profile(
    req: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cập nhật hoặc tạo mới thông tin hồ sơ cá nhân trong bảng UserProfile.
    Sau khi lưu, hệ thống AI Matchmaker sẽ ưu tiên dữ liệu này để so sánh và gợi ý kết nối.
    """
    # 1. Cập nhật User info nếu có
    if req.full_name is not None:
        current_user.full_name = req.full_name
    if req.avatar is not None:
        current_user.avatar = req.avatar
    db.commit()

    # 2. Cập nhật hoặc tạo mới UserProfile record
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    now = datetime.now(timezone.utc)

    if not user_profile:
        user_profile = UserProfile(
            user_id=current_user.id,
            profession=req.profession,
            company=req.company,
            location=req.location,
            skills=req.skills,
            interests=req.interests,
            looking_for=req.looking_for,
            offering=req.offering,
            bio=req.bio,
            created_at=now,
            updated_at=now,
        )
        db.add(user_profile)
    else:
        user_profile.profession = req.profession
        user_profile.company = req.company
        user_profile.location = req.location
        user_profile.skills = req.skills
        user_profile.interests = req.interests
        user_profile.looking_for = req.looking_for
        user_profile.offering = req.offering
        user_profile.bio = req.bio
        user_profile.updated_at = now

    db.commit()
    db.refresh(user_profile)
    db.refresh(current_user)

    return ProfileResponse(
        user_id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar=current_user.avatar,
        profession=user_profile.profession,
        company=user_profile.company,
        location=user_profile.location,
        skills=user_profile.skills or [],
        interests=user_profile.interests or [],
        looking_for=user_profile.looking_for or [],
        offering=user_profile.offering or [],
        bio=user_profile.bio,
        is_custom_profile=True,
        created_at=user_profile.created_at,
        updated_at=user_profile.updated_at,
    )
