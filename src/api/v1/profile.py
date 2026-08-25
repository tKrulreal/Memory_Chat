"""
User Profile API (v1).
Quản lý thông tin hồ sơ cá nhân do người dùng tự nhập để phục vụ tìm kiếm & so khớp gợi ý kết nối.
Hỗ trợ bật/tắt công khai hồ sơ (is_public), thông tin mạng xã hội, kinh nghiệm, học vấn và trang hồ sơ chi tiết.
"""

from datetime import datetime, timezone
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.v1.auth import get_current_user
from src.models.chat import Conversation
from src.models.connection import ConnectionRequest
from src.models.user import User, UserProfile
from src.agents.connection.agent import ConnectionRecommendationAgent

router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    avatar: str | None = None
    gender: str | None = None
    phone: str | None = None
    profession: str | None = Field(default=None, description="Chuyên môn / Chức danh")
    company: str | None = Field(default=None, description="Công ty / Tổ chức công tác")
    location: str | None = Field(default=None, description="Địa điểm / Thành phố (Hà Nội, TP.HCM, ...)")
    skills: list[str] = Field(default_factory=list, description="Danh sách kỹ năng chuyên môn")
    interests: list[str] = Field(default_factory=list, description="Lĩnh vực quan tâm / Sở thích")
    looking_for: list[str] = Field(default_factory=list, description="Nhu cầu tìm kiếm (AI projects, đối tác, tuyển dụng...)")
    offering: list[str] = Field(default_factory=list, description="Thế mạnh có thể đóng góp/chia sẻ")
    bio: str | None = Field(default=None, description="Giới thiệu bản thân ngắn gọn")
    is_public: bool | None = Field(default=True, description="Chế độ công khai hồ sơ trên mạng")
    github: str | None = Field(default=None, description="Link GitHub")
    linkedin: str | None = Field(default=None, description="Link LinkedIn")
    website: str | None = Field(default=None, description="Link Website/Portfolio cá nhân")
    experience: list[dict[str, Any]] = Field(default_factory=list, description="Kinh nghiệm làm việc")
    education: list[dict[str, Any]] = Field(default_factory=list, description="Học vấn / Bằng cấp")


class ProfileResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str | None
    avatar: str | None
    gender: str | None
    phone: str | None
    profession: str | None
    company: str | None
    location: str | None
    skills: list[str]
    interests: list[str]
    looking_for: list[str]
    offering: list[str]
    bio: str | None
    is_public: bool = True
    github: str | None = None
    linkedin: str | None = None
    website: str | None = None
    experience: list[dict[str, Any]] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    is_custom_profile: bool = Field(description="True nếu người dùng đã tự nhập thông tin vào bảng UserProfile")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PublicProfileResponse(BaseModel):
    user_id: uuid.UUID
    email: str | None = None
    full_name: str | None
    avatar: str | None
    gender: str | None = None
    phone: str | None = None
    profession: str | None = None
    company: str | None = None
    location: str | None = None
    skills: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    looking_for: list[str] = Field(default_factory=list)
    offering: list[str] = Field(default_factory=list)
    bio: str | None = None
    is_public: bool = True
    github: str | None = None
    linkedin: str | None = None
    website: str | None = None
    experience: list[dict[str, Any]] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    connection_status: str = Field(description="CONNECTED | PENDING_SENT | PENDING_RECEIVED | NONE")
    conversation_id: str | None = None
    created_at: datetime | None = None


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
        gender=current_user.gender,
        phone=current_user.phone,
        profession=user_profile.profession if (user_profile and user_profile.profession) else unified_dict.get("profession"),
        company=user_profile.company if (user_profile and user_profile.company) else unified_dict.get("company"),
        location=user_profile.location if (user_profile and user_profile.location) else unified_dict.get("location"),
        skills=user_profile.skills if (user_profile and user_profile.skills) else unified_dict.get("skills", []),
        interests=user_profile.interests if (user_profile and user_profile.interests) else unified_dict.get("interests", []),
        looking_for=user_profile.looking_for if (user_profile and user_profile.looking_for) else unified_dict.get("current_needs", []),
        offering=user_profile.offering if (user_profile and user_profile.offering) else unified_dict.get("current_offers", []),
        bio=user_profile.bio if user_profile else None,
        is_public=user_profile.is_public if user_profile and user_profile.is_public is not None else True,
        github=user_profile.github if user_profile else None,
        linkedin=user_profile.linkedin if user_profile else None,
        website=user_profile.website if user_profile else None,
        experience=user_profile.experience if (user_profile and user_profile.experience) else [],
        education=user_profile.education if (user_profile and user_profile.education) else [],
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
    if req.gender is not None:
        current_user.gender = req.gender
    if req.phone is not None:
        current_user.phone = req.phone
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
            is_public=req.is_public if req.is_public is not None else True,
            github=req.github,
            linkedin=req.linkedin,
            website=req.website,
            experience=req.experience,
            education=req.education,
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
        if req.is_public is not None:
            user_profile.is_public = req.is_public
        user_profile.github = req.github
        user_profile.linkedin = req.linkedin
        user_profile.website = req.website
        user_profile.experience = req.experience
        user_profile.education = req.education
        user_profile.updated_at = now

    db.commit()
    db.refresh(user_profile)
    db.refresh(current_user)

    return ProfileResponse(
        user_id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar=current_user.avatar,
        gender=current_user.gender,
        phone=current_user.phone,
        profession=user_profile.profession,
        company=user_profile.company,
        location=user_profile.location,
        skills=user_profile.skills or [],
        interests=user_profile.interests or [],
        looking_for=user_profile.looking_for or [],
        offering=user_profile.offering or [],
        bio=user_profile.bio,
        is_public=user_profile.is_public if user_profile.is_public is not None else True,
        github=user_profile.github,
        linkedin=user_profile.linkedin,
        website=user_profile.website,
        experience=user_profile.experience or [],
        education=user_profile.education or [],
        is_custom_profile=True,
        created_at=user_profile.created_at,
        updated_at=user_profile.updated_at,
    )


@router.get("/{target_user_id}", response_model=PublicProfileResponse)
def get_user_public_profile(
    target_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy thông tin hồ sơ công khai của một người dùng bất kỳ:
    - Kiểm tra trạng thái kết nối (CONNECTED, PENDING_SENT, PENDING_RECEIVED, NONE).
    - Nếu người dùng bật is_public=False và chưa kết nối: Trả về trạng thái riêng tư.
    - Nếu bật is_public=True: Trả về đầy đủ kỹ năng, kinh nghiệm, học vấn, bio.
    """
    target_user = db.get(User, target_user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại.",
        )

    # 1. Kiểm tra quan hệ chat / kết nối
    conv = db.query(Conversation).filter(
        ((Conversation.user_a_id == current_user.id) & (Conversation.user_b_id == target_user_id)) |
        ((Conversation.user_a_id == target_user_id) & (Conversation.user_b_id == current_user.id))
    ).first()

    conversation_id = str(conv.id) if conv else None
    connection_status = "CONNECTED" if conv else "NONE"

    if not conv and target_user_id != current_user.id:
        req = db.query(ConnectionRequest).filter(
            ((ConnectionRequest.sender_id == current_user.id) & (ConnectionRequest.receiver_id == target_user_id)) |
            ((ConnectionRequest.sender_id == target_user_id) & (ConnectionRequest.receiver_id == current_user.id))
        ).first()

        if req:
            if req.status == "ACCEPTED":
                connection_status = "CONNECTED"
            elif req.status == "PENDING":
                if req.sender_id == current_user.id:
                    connection_status = "PENDING_SENT"
                else:
                    connection_status = "PENDING_RECEIVED"

    # 2. Lấy profile
    prof = db.query(UserProfile).filter(UserProfile.user_id == target_user_id).first()
    is_public = prof.is_public if prof and prof.is_public is not None else True

    # 3. Nếu là profile riêng tư và chưa kết nối và không phải chính mình
    if not is_public and connection_status != "CONNECTED" and target_user_id != current_user.id:
        return PublicProfileResponse(
            user_id=target_user.id,
            email=None,
            full_name=target_user.full_name or "Người dùng MemoryChat",
            avatar=target_user.avatar,
            gender=None,
            phone=None,
            profession=prof.profession if prof else None,
            company=prof.company if prof else None,
            location=None,
            skills=[],
            interests=[],
            looking_for=[],
            offering=[],
            bio="Hồ sơ này đang được đặt ở chế độ riêng tư.",
            is_public=False,
            github=None,
            linkedin=None,
            website=None,
            experience=[],
            education=[],
            connection_status=connection_status,
            conversation_id=conversation_id,
            created_at=target_user.created_at,
        )

    # 4. Trả về hồ sơ công khai đầy đủ
    return PublicProfileResponse(
        user_id=target_user.id,
        email=target_user.email if is_public else None,
        full_name=target_user.full_name or target_user.email,
        avatar=target_user.avatar,
        gender=target_user.gender if is_public else None,
        phone=target_user.phone if is_public else None,
        profession=prof.profession if prof else None,
        company=prof.company if prof else None,
        location=prof.location if prof else None,
        skills=prof.skills if (prof and prof.skills) else [],
        interests=prof.interests if (prof and prof.interests) else [],
        looking_for=prof.looking_for if (prof and prof.looking_for) else [],
        offering=prof.offering if (prof and prof.offering) else [],
        bio=prof.bio if prof else None,
        is_public=is_public,
        github=prof.github if prof else None,
        linkedin=prof.linkedin if prof else None,
        website=prof.website if prof else None,
        experience=prof.experience if (prof and prof.experience) else [],
        education=prof.education if (prof and prof.education) else [],
        connection_status=connection_status,
        conversation_id=conversation_id,
        created_at=target_user.created_at,
    )
