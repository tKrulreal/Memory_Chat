"""
API endpoints for Connection Recommendations (User-to-User Networking).
"""

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from src.agents.connection import ConnectionRecommendationAgent
from src.agents.connection.schemas import (
    AcceptConnectionRequest,
    ConnectionRecommendation,
    ConnectionRecommendationDetail,
    GenerateConnectionsResponse,
)
from src.api.deps import get_db
from src.core.security import get_current_user
from src.models.user import User
from src.models.ai import Recommendation, AssistantMemory
from src.models.chat import Conversation, ConversationUserState, Message
from src.models.contact import Contact, ContactMemory
from src.models.tag import AISystemConfig
from src.schemas.enums import RecommendationType

router = APIRouter(prefix="/recommendations/connections", tags=["connections"])


def get_connection_agent() -> ConnectionRecommendationAgent:
    return ConnectionRecommendationAgent()


CurrentUserDep = Annotated[User, Depends(get_current_user)]
DatabaseDep = Annotated[Session, Depends(get_db)]
ConnectionAgentDep = Annotated[ConnectionRecommendationAgent, Depends(get_connection_agent)]


@router.get("", response_model=list[ConnectionRecommendation])
async def list_connections(
    current_user: CurrentUserDep,
    db: DatabaseDep,
    status_filter: str = Query(default="PENDING", alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    Lấy danh sách các gợi ý kết nối dành cho bản thân người dùng hiện tại do AI đánh giá thật.
    """
    # Read AI config for min_score filter
    min_score_percent = 50
    ai_config = db.query(AISystemConfig).filter(
        AISystemConfig.user_id == current_user.id,
        AISystemConfig.key == "ai_settings"
    ).first()
    if ai_config and isinstance(ai_config.value, dict):
        min_score_percent = int(ai_config.value.get("min_matching_score", 50))
        
    query = (
        db.query(Recommendation)
        .filter(
            Recommendation.owner_user_id == current_user.id,
            Recommendation.type == RecommendationType.CONNECTION.value,
            Recommendation.confidence >= (min_score_percent / 100.0)
        )
    )

    if status_filter != "ALL":
        query = query.filter(Recommendation.status == status_filter)

    recommendations = (
        query
        .order_by(Recommendation.confidence.desc(), Recommendation.created_at.desc())
        .limit(limit)
        .all()
    )

    agent = ConnectionRecommendationAgent()

    # If user has no pending recommendations yet, trigger dynamic AI evaluation in real time
    if (status_filter == "PENDING" or status_filter == "ALL") and not recommendations:
        # Only auto-generate if AI and Recommendation feature are enabled
        can_generate = True
        
        if not current_user.setting or not current_user.setting.ai_enabled:
            can_generate = False
            
        if ai_config and isinstance(ai_config.value, dict):
            features = ai_config.value.get("features", {})
            if features.get("recommendation") is False:
                can_generate = False
            
        if can_generate:
            try:
                await agent.generate(current_user.id, min_score=min_score_percent / 100.0, limit=5)
                recommendations = (
                    query
                    .order_by(Recommendation.confidence.desc(), Recommendation.created_at.desc())
                    .limit(limit)
                    .all()
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Auto AI generation error for user {current_user.id}: {e}")

    results = []
    for rec in recommendations:
        # Check target user
        target_user = None
        if rec.target_user_id:
            target_user = db.get(User, rec.target_user_id)
        elif rec.target_contact_id:
            contact_b = db.get(Contact, rec.target_contact_id)
            if contact_b:
                target_user = User(
                    id=contact_b.id,
                    email=contact_b.email or "contact@example.com",
                    full_name=contact_b.display_name,
                    avatar=contact_b.avatar_url,
                )

        target_name = target_user.full_name or (target_user.email.split("@")[0] if target_user else "Người dùng")
        target_email = target_user.email if target_user else ""
        target_avatar = target_user.avatar if target_user else None

        # Extract target profile
        target_profession = None
        target_company = None
        target_location = None
        target_skills: list[str] = []
        target_interests: list[str] = []
        target_needs: list[str] = []
        target_offers: list[str] = []

        if target_user and target_user.id:
            profile = agent.extract_user_profile(target_user, db)
            target_profession = profile["profession"]
            target_company = profile["company"]
            target_location = profile.get("location")
            target_skills = profile["skills"]
            target_interests = profile["interests"]
            target_needs = profile.get("current_needs", [])
            target_offers = profile.get("current_offers", [])

        item = ConnectionRecommendation(
            id=rec.id,
            owner_user_id=rec.owner_user_id,
            target_user_id=rec.target_user_id or (target_user.id if target_user else uuid.UUID(int=0)),
            reason=rec.reason,
            priority=rec.priority,
            confidence=rec.confidence,
            status=rec.status,
            created_at=rec.created_at,
            expires_at=rec.expires_at,
            target_user_name=target_name,
            target_user_email=target_email,
            target_user_avatar=target_avatar,
            target_user_profession=target_profession,
            target_user_company=target_company,
            target_user_location=target_location,
            target_user_skills=target_skills,
            target_user_interests=target_interests,
            target_user_needs=target_needs,
            target_user_offers=target_offers,
            target_contact_name=target_name,
            contact_name=current_user.full_name or current_user.email,
        )
        results.append(item)

    # Sort results strictly from highest match score to lowest
    results.sort(key=lambda r: (r.confidence or 0.0), reverse=True)

    return results


@router.get("/{recommendation_id}", response_model=ConnectionRecommendationDetail)

def get_connection_detail(
    recommendation_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
):
    """
    Lấy chi tiết so sánh giữa Người dùng hiện tại và Người dùng được gợi ý.
    """
    rec = (
        db.query(Recommendation)
        .filter(
            Recommendation.id == recommendation_id,
            Recommendation.owner_user_id == current_user.id,
            Recommendation.type == RecommendationType.CONNECTION.value,
        )
        .first()
    )

    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    agent = ConnectionRecommendationAgent()

    # 1. Profile của Current User (Bản thân)
    current_profile = agent.extract_user_profile(current_user, db)

    # 2. Profile của Target User (Người được gợi ý)
    target_user = None
    if rec.target_user_id:
        target_user = db.get(User, rec.target_user_id)
    elif rec.target_contact_id:
        contact_b = db.get(Contact, rec.target_contact_id)
        if contact_b:
            target_user = User(
                id=contact_b.id,
                email=contact_b.email or "contact@example.com",
                full_name=contact_b.display_name,
                avatar=contact_b.avatar_url,
            )

    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")

    target_profile = agent.extract_user_profile(target_user, db)

    # 3. Check existing conversation
    existing_conv = (
        db.query(Conversation)
        .filter(
            or_(
                and_(Conversation.user_a_id == current_user.id, Conversation.user_b_id == target_user.id),
                and_(Conversation.user_a_id == target_user.id, Conversation.user_b_id == current_user.id),
            )
        )
        .first()
    )

    suggested_intro = f"Chào {target_profile['full_name']}, mình thấy bạn đang làm việc về {', '.join(target_profile['interests'][:2])}. Mình cũng rất quan tâm và muốn kết nối để trao đổi thêm cùng bạn!"

    return ConnectionRecommendationDetail(
        id=rec.id,
        reason=rec.reason,
        priority=rec.priority,
        confidence=rec.confidence,
        status=rec.status,
        created_at=rec.created_at,
        # Current User (You)
        current_user_id=current_user.id,
        current_user_name=current_profile["full_name"],
        current_user_email=current_profile["email"],
        current_user_profession=current_profile["profession"],
        current_user_company=current_profile["company"],
        current_user_location=current_profile.get("location"),
        current_user_skills=current_profile["skills"],
        current_user_interests=current_profile["interests"],
        current_user_needs=current_profile["current_needs"],
        current_user_offers=current_profile["current_offers"],
        # Target User (The Person to Connect With)
        target_user_id=target_user.id,
        target_user_name=target_profile["full_name"],
        target_user_email=target_profile["email"],
        target_user_avatar=target_profile["avatar"],
        target_user_profession=target_profile["profession"],
        target_user_company=target_profile["company"],
        target_user_location=target_profile.get("location"),
        target_user_skills=target_profile["skills"],
        target_user_interests=target_profile["interests"],
        target_user_needs=target_profile["current_needs"],
        target_user_offers=target_profile["current_offers"],
        target_user_bio=target_profile.get("summary"),
        suggested_intro=suggested_intro,
        conversation_id=existing_conv.id if existing_conv else None,
        # Legacy aliases
        contact_a_id=current_user.id,
        contact_a_name=current_profile["full_name"],
        contact_a_profession=current_profile["profession"],
        contact_a_company=current_profile["company"],
        contact_b_id=target_user.id,
        contact_b_name=target_profile["full_name"],
        contact_b_profession=target_profile["profession"],
        contact_b_company=target_profile["company"],
    )



@router.post("/{recommendation_id}/accept", response_model=ConnectionRecommendation)
def accept_connection(
    recommendation_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    request: AcceptConnectionRequest | None = None,
):
    """
    Chấp nhận một connection recommendation:
    1. Cập nhật trạng thái Recommendation thành ACCEPTED.
    2. Tự động gửi một ConnectionRequest đến Target User.
    """
    from src.models.connection import ConnectionRequest
    rec = (
        db.query(Recommendation)
        .filter(
            Recommendation.id == recommendation_id,
            Recommendation.owner_user_id == current_user.id,
            Recommendation.type == RecommendationType.CONNECTION.value,
        )
        .first()
    )

    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    if rec.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recommendation already processed")

    # Update status
    rec.status = "ACCEPTED"

    # Identify target user
    target_user = None
    if rec.target_user_id:
        target_user = db.get(User, rec.target_user_id)

    intro_content = (
        request.custom_message
        if request and request.custom_message
        else f"Xin chào! Mình vừa nhận được gợi ý kết nối với bạn qua MemoryChat và rất mong có cơ hội trò chuyện cùng bạn."
    )

    target_conv_id = None
    # If target user is a real user, create a Connection Request
    if target_user:
        # Check if already connected or pending
        existing_conv = (
            db.query(Conversation)
            .filter(
                or_(
                    and_(Conversation.user_a_id == current_user.id, Conversation.user_b_id == target_user.id),
                    and_(Conversation.user_a_id == target_user.id, Conversation.user_b_id == current_user.id),
                )
            )
            .first()
        )
        if existing_conv:
            target_conv_id = existing_conv.id
        else:
            existing_req = db.query(ConnectionRequest).filter(
                or_(
                    and_(ConnectionRequest.sender_id == current_user.id, ConnectionRequest.receiver_id == target_user.id),
                    and_(ConnectionRequest.sender_id == target_user.id, ConnectionRequest.receiver_id == current_user.id),
                ),
                ConnectionRequest.status == "PENDING"
            ).first()
            if not existing_req:
                new_req = ConnectionRequest(
                    sender_id=current_user.id,
                    receiver_id=target_user.id,
                    status="PENDING"
                )
                db.add(new_req)
            elif existing_req.sender_id == target_user.id:
                # Target user already sent a request, so accept it!
                existing_req.status = "ACCEPTED"
                new_conv = Conversation(user_a_id=existing_req.sender_id, user_b_id=existing_req.receiver_id)
                db.add(new_conv)
                db.flush()
                target_conv_id = new_conv.id

    db.commit()
    db.refresh(rec)

    return ConnectionRecommendation(
        id=rec.id,
        owner_user_id=rec.owner_user_id,
        target_user_id=rec.target_user_id or uuid.UUID(int=0),
        reason=rec.reason,
        priority=rec.priority,
        confidence=rec.confidence,
        status=rec.status,
        created_at=rec.created_at,
        expires_at=rec.expires_at,
        target_user_name=target_user.full_name if target_user else None,
        target_user_email=target_user.email if target_user else None,
        conversation_id=target_conv_id if target_user else None,
    )


@router.post("/{recommendation_id}/reject", response_model=ConnectionRecommendation)
def reject_connection(
    recommendation_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
):
    """Từ chối một connection recommendation."""
    rec = (
        db.query(Recommendation)
        .filter(
            Recommendation.id == recommendation_id,
            Recommendation.owner_user_id == current_user.id,
            Recommendation.type == RecommendationType.CONNECTION.value,
        )
        .first()
    )

    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    if rec.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recommendation already processed")

    rec.status = "REJECTED"
    db.commit()
    db.refresh(rec)

    return ConnectionRecommendation(
        id=rec.id,
        owner_user_id=rec.owner_user_id,
        target_user_id=rec.target_user_id,
        reason=rec.reason,
        priority=rec.priority,
        confidence=rec.confidence,
        status=rec.status,
        created_at=rec.created_at,
        expires_at=rec.expires_at,
    )


@router.post("/dismiss/{recommendation_id}", response_model=ConnectionRecommendation)
def dismiss_connection(
    recommendation_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
):
    """Bỏ qua một recommendation."""
    rec = (
        db.query(Recommendation)
        .filter(
            Recommendation.id == recommendation_id,
            Recommendation.owner_user_id == current_user.id,
            Recommendation.type == RecommendationType.CONNECTION.value,
        )
        .first()
    )

    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    rec.status = "DISMISSED"
    db.commit()
    db.refresh(rec)

    return ConnectionRecommendation(
        id=rec.id,
        owner_user_id=rec.owner_user_id,
        target_user_id=rec.target_user_id,
        reason=rec.reason,
        priority=rec.priority,
        confidence=rec.confidence,
        status=rec.status,
        created_at=rec.created_at,
        expires_at=rec.expires_at,
    )


@router.post("/generate", response_model=GenerateConnectionsResponse)
async def generate_connections(
    current_user: CurrentUserDep,
    db: DatabaseDep,
    agent: ConnectionAgentDep,
    force_refresh: bool = Query(default=True, description="Xoá các gợi ý PENDING cũ để đánh giá lại từ đầu"),
):
    """
    Trigger phân tích AI tự động tìm người dùng thật trong hệ thống phù hợp với User hiện tại.
    """
    try:
        # Check global toggle
        if not current_user.setting or not current_user.setting.ai_enabled:
            raise HTTPException(status_code=400, detail="Tính năng AI đang bị tắt.")
            
        # Check specific recommendation toggle
        ai_config = db.query(AISystemConfig).filter(
            AISystemConfig.user_id == current_user.id,
            AISystemConfig.key == "ai_settings"
        ).first()
        
        min_score_percent = 50
        if ai_config and isinstance(ai_config.value, dict):
            features = ai_config.value.get("features", {})
            if features.get("recommendation") is False:
                raise HTTPException(status_code=400, detail="Tính năng Gợi ý kết nối (AI Recommendation) đã bị tắt.")
            min_score_percent = int(ai_config.value.get("min_matching_score", 50))

        if force_refresh:
            old_pending = db.query(Recommendation).filter(
                Recommendation.owner_user_id == current_user.id,
                Recommendation.type == RecommendationType.CONNECTION.value,
                Recommendation.status == "PENDING"
            ).all()
            for rec in old_pending:
                db.delete(rec)
            db.commit()

        recommendations = await agent.generate(
            user_id=current_user.id,
            min_score=min_score_percent / 100.0,
            limit=10,
        )

        total_pending = (
            db.query(Recommendation)
            .filter(
                Recommendation.owner_user_id == current_user.id,
                Recommendation.type == RecommendationType.CONNECTION.value,
                Recommendation.status == "PENDING",
            )
            .count()
        )

        return GenerateConnectionsResponse(
            generated=len(recommendations),
            total_pending=total_pending,
            message=f"Đã tìm thấy {len(recommendations)} người dùng phù hợp để kết nối với bạn!" if recommendations else "Chưa có thêm người dùng mới phù hợp trong hệ thống.",
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
