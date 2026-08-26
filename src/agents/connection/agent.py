"""
Connection Recommendation Agent (User-to-User Networking).

Pipeline 5 bước:
Bước 1: SQL Hard Filter (loại chính mình, bạn bè đã chat, lời mời pending/accepted, user bị block 2 chiều, profile is_public=False / ai_read_profile=False).
Bước 2: Candidate Retrieval (Profile Embedding & Qdrant Vector Search -> Top 50/100).
Bước 3: Feature Engineering (Semantic, Skill, Interest, Goal Synergy, Location, Activity).
Bước 4: Weighted Scoring (0.30 Semantic + 0.25 Skill + 0.15 Interest + 0.15 Goal + 0.10 Location + 0.05 Activity -> Top 5).
Bước 5: Targeted LLM (Chỉ đưa Top 5 vào LLM để sinh reason, suggested_intro, complementary_aspects).
"""

import json
import logging
import math
import re
import unicodedata
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from src.agents.connection.prompts import (
    ANALYZE_USER_PROFILE_PROMPT,
    COMPARE_USERS_PROMPT,
    GENERATE_MATCH_REASON_PROMPT,
)
from src.agents.connection.schemas import (
    UserProfileDict,
    ConnectionRecommendation as ConnectionRecommendationSchema,
    ConnectionRecommendationDetail,
)
from src.gateways.llm import LLMGateway
from src.models.database import SessionLocal
from src.models.user import User, UserProfile, UserBlock, Setting
from src.models.ai import AssistantMemory, Recommendation
from src.models.chat import Conversation, Message
from src.models.connection import ConnectionRequest
from src.models.contact import Contact
from src.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


@dataclass
class FeatureScores:
    """Breakdown of individual feature match scores."""
    semantic: float = 0.0
    skill: float = 0.0
    interest: float = 0.0
    goal: float = 0.0
    location: float = 0.0
    activity: float = 0.0
    composite_score: float = 0.0


@dataclass
class UserMatchResult:
    """Result of matching current user with a candidate real user."""
    candidate_user_id: uuid.UUID
    match_score: float
    priority: str
    reason: str
    suggested_intro: str
    complementary_aspects: list[str] = field(default_factory=list)
    shared_interests: list[str] = field(default_factory=list)
    feature_scores: FeatureScores | None = None


def _remove_accents(text: str) -> str:
    """Remove Vietnamese diacritical marks."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    no_accents = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return no_accents.replace("đ", "d").replace("Đ", "d")


def _normalize_text(text: str) -> str:
    """Normalize string for token and keyword comparison."""
    if not text:
        return ""
    text = _remove_accents(text.lower().strip())
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    score = dot / (norm_a * norm_b)
    return max(0.0, min(1.0, (score + 1.0) / 2.0))


def _calculate_jaccard(items_a: list[str], items_b: list[str]) -> float:
    """Calculate token-level Jaccard similarity between two string lists."""
    if not items_a or not items_b:
        return 0.0
    tokens_a = set()
    for it in items_a:
        tokens_a.update(_normalize_text(it).split())
    tokens_b = set()
    for it in items_b:
        tokens_b.update(_normalize_text(it).split())

    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    if not union:
        return 0.0
    return len(intersection) / len(union)


def _calculate_goal_synergy(
    needs_a: list[str], offers_a: list[str], skills_a: list[str],
    needs_b: list[str], offers_b: list[str], skills_b: list[str]
) -> float:
    """
    Calculate mutual goal / need vs offer synergy:
    Does User A's looking_for match User B's offering/skills, and vice versa?
    """
    tokens_need_a = set()
    for it in needs_a:
        tokens_need_a.update(_normalize_text(it).split())
    tokens_cap_b = set()
    for it in (offers_b + skills_b):
        tokens_cap_b.update(_normalize_text(it).split())

    match_a_to_b = (len(tokens_need_a & tokens_cap_b) / len(tokens_need_a)) if tokens_need_a else 0.0

    tokens_need_b = set()
    for it in needs_b:
        tokens_need_b.update(_normalize_text(it).split())
    tokens_cap_a = set()
    for it in (offers_a + skills_a):
        tokens_cap_a.update(_normalize_text(it).split())

    match_b_to_a = (len(tokens_need_b & tokens_cap_a) / len(tokens_need_b)) if tokens_need_b else 0.0

    if tokens_need_a and tokens_need_b:
        return min(1.0, 0.6 * match_a_to_b + 0.4 * match_b_to_a)
    elif tokens_need_a:
        return min(1.0, match_a_to_b)
    elif tokens_need_b:
        return min(1.0, match_b_to_a)
    else:
        return 0.1


def _calculate_location_score(loc_a: str | None, loc_b: str | None) -> float:
    """Calculate location compatibility score."""
    if not loc_a or not loc_b:
        return 0.3
    norm_a = _normalize_text(loc_a)
    norm_b = _normalize_text(loc_b)
    if not norm_a or not norm_b:
        return 0.3

    hanoi_synonyms = {"ha noi", "hanoi", "hn"}
    hcm_synonyms = {"ho chi minh", "tp ho chi minh", "tphcm", "tp hcm", "saigon", "sai gon"}
    danang_synonyms = {"da nang", "danang"}

    is_hn_a = any(s in norm_a for s in hanoi_synonyms)
    is_hn_b = any(s in norm_b for s in hanoi_synonyms)
    if is_hn_a and is_hn_b:
        return 1.0

    is_hcm_a = any(s in norm_a for s in hcm_synonyms)
    is_hcm_b = any(s in norm_b for s in hcm_synonyms)
    if is_hcm_a and is_hcm_b:
        return 1.0

    is_dn_a = any(s in norm_a for s in danang_synonyms)
    is_dn_b = any(s in norm_b for s in danang_synonyms)
    if is_dn_a and is_dn_b:
        return 1.0

    if norm_a in norm_b or norm_b in norm_a:
        return 1.0

    if ("viet nam" in norm_a or "vietnam" in norm_a) and ("viet nam" in norm_b or "vietnam" in norm_b):
        return 0.5

    return 0.0


def _calculate_activity_score(user: User) -> float:
    """Calculate user activity recency score."""
    last_active = user.updated_at or user.created_at
    if not last_active:
        return 0.2
    now = datetime.now(timezone.utc)
    if last_active.tzinfo is None:
        last_active = last_active.replace(tzinfo=timezone.utc)
    diff = (now - last_active).total_seconds()
    if diff <= 86400:  # <= 24 hours
        return 1.0
    elif diff <= 7 * 86400:  # <= 7 days
        return 0.8
    elif diff <= 30 * 86400:  # <= 30 days
        return 0.5
    else:
        return 0.2


class ConnectionRecommendationAgent:
    """
    Multi-stage Connection Recommendation Agent (User-to-User Networking).
    """

    def __init__(self, llm: LLMGateway | None = None, vector_store: VectorStoreService | None = None):
        self._llm = llm or LLMGateway()
        self._vector_store = vector_store or VectorStoreService.get_instance()

    def _parse_json_response(self, raw: str) -> dict[str, Any] | None:
        """Parse JSON an toàn từ LLM response."""
        if not raw:
            return None

        # 1. Direct json
        try:
            return json.loads(raw)
        except Exception:
            pass

        # 2. Extract from markdown code block
        match = re.search(r"```(?:json)?\s*([\s\S]+?)```", raw)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except Exception:
                pass

        # 3. Extract JSON-like { ... }
        match = re.search(r"\{[\s\S]+\}", raw)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass

        return None

    def _format_bullets(self, items: list[str], default_text: str = "Chưa rõ") -> str:
        """Chuyển đổi mảng chuỗi thành danh sách gạch đầu dòng Markdown."""
        if not items:
            return f"- {default_text}"
        return "\n".join([f"- {item}" for item in items])

    def extract_user_profile(self, user: User, db: Session) -> UserProfileDict:
        """
        Trích xuất hồ sơ người dùng:
        1. Ưu tiên 1 (Cao nhất): Dữ liệu do chính người dùng tự nhập trong bảng UserProfile.
        2. Ưu tiên 2 (Tự động trích xuất): Từ AssistantMemory & Messages nếu thiếu.
        """
        setting = user.setting
        if setting and getattr(setting, "ai_read_profile", True) is False:
            return UserProfileDict(
                user_id=str(user.id),
                email=user.email,
                full_name=user.full_name or user.email.split("@")[0],
                avatar=user.avatar,
                profession=None,
                company=None,
                location=None,
                skills=[],
                interests=[],
                current_needs=[],
                current_offers=[],
                summary="Hồ sơ được bảo mật theo yêu cầu người dùng.",
            )

        collected_skills: list[str] = []
        collected_interests: list[str] = []
        collected_needs: list[str] = []
        collected_offers: list[str] = []
        profession: str | None = None
        company: str | None = None
        location: str | None = None
        bio: str | None = None

        # 1. Đọc UserProfile
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        if user_profile:
            if user_profile.profession:
                profession = user_profile.profession
            if user_profile.company:
                company = user_profile.company
            if user_profile.location:
                location = user_profile.location
            if user_profile.skills and isinstance(user_profile.skills, list):
                collected_skills.extend(user_profile.skills)
            if user_profile.interests and isinstance(user_profile.interests, list):
                collected_interests.extend(user_profile.interests)
            if user_profile.looking_for and isinstance(user_profile.looking_for, list):
                collected_needs.extend(user_profile.looking_for)
            if user_profile.offering and isinstance(user_profile.offering, list):
                collected_offers.extend(user_profile.offering)
            if user_profile.bio:
                bio = user_profile.bio

        # 2. Assistant Memories nếu còn thiếu
        memories = (
            db.query(AssistantMemory)
            .filter(AssistantMemory.owner_user_id == user.id)
            .order_by(AssistantMemory.updated_at.desc())
            .limit(10)
            .all()
        )
        memories_summary = "\n".join([m.summary for m in memories if m.summary]) or "Chưa có hội thoại trợ lý"

        for m in memories:
            if m.facts and isinstance(m.facts, dict):
                if not profession and m.facts.get("profession"):
                    profession = str(m.facts["profession"])
                if not company and m.facts.get("company"):
                    company = str(m.facts["company"])
                if not location and m.facts.get("location"):
                    location = str(m.facts["location"])
                if not collected_skills and isinstance(m.facts.get("skills"), list):
                    collected_skills.extend([str(s) for s in m.facts["skills"]])
                if not collected_interests and isinstance(m.facts.get("interested_in"), list):
                    collected_interests.extend([str(i) for i in m.facts["interested_in"]])
                if not collected_interests and isinstance(m.facts.get("interests"), list):
                    collected_interests.extend([str(i) for i in m.facts["interests"]])
                if not collected_needs and isinstance(m.facts.get("looking_for"), list):
                    collected_needs.extend([str(n) for n in m.facts["looking_for"]])
                if not collected_needs and isinstance(m.facts.get("current_needs"), list):
                    collected_needs.extend([str(n) for n in m.facts["current_needs"]])
                if not collected_offers and isinstance(m.facts.get("offering"), list):
                    collected_offers.extend([str(o) for o in m.facts["offering"]])
                if not collected_offers and isinstance(m.facts.get("current_offers"), list):
                    collected_offers.extend([str(o) for o in m.facts["current_offers"]])

        # 3. Tin nhắn do user gửi đi
        recent_msgs = (
            db.query(Message)
            .filter(Message.sender_user_id == user.id)
            .order_by(Message.created_at.desc())
            .limit(20)
            .all()
        )
        recent_messages_text = "\n".join([f"- {msg.content}" for msg in recent_msgs if msg.content and msg.content.strip()]) or "Chưa gửi tin nhắn nào"

        # 4. Contact record
        if not profession or not company:
            contact_record = db.query(Contact).filter(Contact.owner_user_id == user.id).first()
            if contact_record:
                profession = profession or contact_record.profession
                company = company or contact_record.company

        # 5. LLM extraction nếu profile còn trống
        if (not collected_skills or not collected_interests or not profession) and recent_messages_text != "Chưa gửi tin nhắn nào":
            prompt = ANALYZE_USER_PROFILE_PROMPT.format(
                full_name=user.full_name or user.email.split("@")[0],
                email=user.email,
                recent_messages=recent_messages_text,
                extra_notes="Không có",
            )
            try:
                response = self._llm.complete(prompt)
                parsed = self._parse_json_response(response)
                if parsed:
                    profession = profession or parsed.get("profession")
                    company = company or parsed.get("company")
                    location = location or parsed.get("location")
                    bio = bio or parsed.get("bio")
                    if not collected_skills and parsed.get("skills"):
                        collected_skills.extend([s for s in parsed.get("skills", []) if s and str(s).strip()])
                    if not collected_interests and parsed.get("interests"):
                        collected_interests.extend([i for i in parsed.get("interests", []) if i and str(i).strip()])
                    if not collected_needs and (parsed.get("looking_for") or parsed.get("current_needs")):
                        collected_needs.extend([n for n in (parsed.get("looking_for") or parsed.get("current_needs") or []) if n and str(n).strip()])
                    if not collected_offers and (parsed.get("offering") or parsed.get("current_offers")):
                        collected_offers.extend([o for o in (parsed.get("offering") or parsed.get("current_offers") or []) if o and str(o).strip()])
            except Exception as e:
                logger.warning(f"Failed LLM profile extraction for user {user.id}: {e}")

        # 6. Auto-cache vào UserProfile
        auto_filled = False
        if not user_profile:
            user_profile = UserProfile(user_id=user.id)
            db.add(user_profile)
            auto_filled = True

        if not user_profile.profession and profession:
            user_profile.profession = profession
            auto_filled = True
        if not user_profile.company and company:
            user_profile.company = company
            auto_filled = True
        if not user_profile.location and location:
            user_profile.location = location
            auto_filled = True
        if not user_profile.skills and collected_skills:
            user_profile.skills = list(dict.fromkeys(collected_skills))
            auto_filled = True
        if not user_profile.interests and collected_interests:
            user_profile.interests = list(dict.fromkeys(collected_interests))
            auto_filled = True
        if not user_profile.looking_for and collected_needs:
            user_profile.looking_for = list(dict.fromkeys(collected_needs))
            auto_filled = True
        if not user_profile.offering and collected_offers:
            user_profile.offering = list(dict.fromkeys(collected_offers))
            auto_filled = True
        if not user_profile.bio and bio:
            user_profile.bio = bio
            auto_filled = True

        if auto_filled:
            try:
                db.commit()
                db.refresh(user_profile)
            except Exception as e:
                logger.warning(f"Failed to auto-save profile for user {user.id}: {e}")
                db.rollback()

        display_name = user.full_name or user.email.split("@")[0]

        return UserProfileDict(
            user_id=str(user.id),
            email=user.email,
            full_name=display_name,
            avatar=user.avatar,
            profession=profession,
            company=company,
            location=location,
            skills=list(dict.fromkeys(collected_skills)),
            interests=list(dict.fromkeys(collected_interests)),
            current_needs=list(dict.fromkeys(collected_needs)),
            current_offers=list(dict.fromkeys(collected_offers)),
            summary=memories_summary if memories_summary != "Chưa có hội thoại trợ lý" else (bio or None),
        )

    def build_profile_text(self, profile: UserProfileDict) -> str:
        """Tạo chuỗi văn bản hồ sơ cá nhân để embed vector."""
        skills_str = ", ".join(profile.get("skills", [])) or "Chưa cập nhật"
        interests_str = ", ".join(profile.get("interests", [])) or "Chưa cập nhật"
        needs_str = ", ".join(profile.get("current_needs", [])) or "Không có nhu cầu cụ thể"
        offers_str = ", ".join(profile.get("current_offers", [])) or "Không có chia sẻ cụ thể"
        return (
            f"Họ tên: {profile.get('full_name', '')}. "
            f"Nghề nghiệp: {profile.get('profession', 'Chuyên gia')}. "
            f"Công ty: {profile.get('company', 'Doanh nghiệp')}. "
            f"Địa điểm: {profile.get('location', 'Việt Nam')}. "
            f"Kỹ năng: {skills_str}. "
            f"Sở thích: {interests_str}. "
            f"Đang tìm kiếm: {needs_str}. "
            f"Đang cung cấp: {offers_str}. "
            f"Bio: {profile.get('summary', '')}"
        )

    # =========================================================================
    # BƯỚC 1: SQL Hard Filter
    # =========================================================================
    def get_candidate_users(self, user_id: uuid.UUID, db: Session) -> list[User]:
        """
        Bước 1: SQL Hard Filter.
        - Loại chính mình
        - Loại bạn bè hiện tại (đã có đoạn chat)
        - Loại lời mời đã gửi / đã nhận (PENDING, ACCEPTED)
        - Loại user bị block (chặn 2 chiều)
        - Loại profile không cho phép discover (is_public=False, ai_read_profile=False)
        """
        # 1. Loại bạn bè hiện tại (Conversation)
        existing_convs = (
            db.query(Conversation)
            .filter(
                or_(
                    Conversation.user_a_id == user_id,
                    Conversation.user_b_id == user_id,
                )
            )
            .all()
        )
        excluded_user_ids = {user_id}
        for c in existing_convs:
            excluded_user_ids.add(c.user_a_id)
            excluded_user_ids.add(c.user_b_id)

        # 2. Loại lời mời kết nối (ConnectionRequest: PENDING, ACCEPTED)
        existing_reqs = (
            db.query(ConnectionRequest)
            .filter(
                or_(
                    ConnectionRequest.sender_id == user_id,
                    ConnectionRequest.receiver_id == user_id,
                )
            )
            .all()
        )
        for req in existing_reqs:
            if req.status in ["PENDING", "ACCEPTED"]:
                excluded_user_ids.add(req.sender_id)
                excluded_user_ids.add(req.receiver_id)

        # 3. Loại gợi ý kết nối PENDING đang chờ
        existing_recs = (
            db.query(Recommendation)
            .filter(
                Recommendation.owner_user_id == user_id,
                Recommendation.type == "CONNECTION",
                Recommendation.status == "PENDING",
            )
            .all()
        )
        for r in existing_recs:
            if r.target_user_id:
                excluded_user_ids.add(r.target_user_id)

        # 4. Loại user bị block (2 chiều: user_id chặn hoặc bị người khác chặn)
        blocks = (
            db.query(UserBlock)
            .filter(
                or_(
                    UserBlock.blocker_id == user_id,
                    UserBlock.blocked_id == user_id,
                )
            )
            .all()
        )
        for b in blocks:
            excluded_user_ids.add(b.blocker_id)
            excluded_user_ids.add(b.blocked_id)

        # 5. Query các User thỏa mãn:
        # - Không nằm trong excluded_user_ids
        # - Setting.ai_read_profile != False
        # - UserProfile.is_public != False
        query = (
            db.query(User)
            .outerjoin(Setting, User.id == Setting.user_id)
            .outerjoin(UserProfile, User.id == UserProfile.user_id)
            .filter(
                ~User.id.in_(excluded_user_ids),
                or_(Setting.ai_read_profile.is_(True), Setting.user_id.is_(None)),
                or_(UserProfile.is_public.is_(True), UserProfile.user_id.is_(None)),
            )
        )
        candidates = query.all()
        return candidates

    # =========================================================================
    # BƯỚC 2: Candidate Retrieval (Qdrant Vector Search)
    # =========================================================================
    def retrieve_candidates(
        self,
        current_profile: UserProfileDict,
        candidate_users: list[User],
        db: Session,
        top_k: int = 50,
    ) -> list[tuple[User, UserProfileDict, float]]:
        """
        Bước 2: Candidate Retrieval.
        Profile → Embedding → Qdrant → Lấy Top 50/100 ứng viên.
        Trả về danh sách: [(candidate_user, candidate_profile, semantic_score)]
        """
        if not candidate_users:
            return []

        # 1. Tạo embedding cho hồ sơ người dùng hiện tại
        current_text = self.build_profile_text(current_profile)
        query_embedding: list[float] = []
        try:
            query_embedding = self._llm.embed(current_text)
        except Exception as e:
            logger.warning(f"Failed to embed current profile: {e}")

        # 2. Chuẩn bị map các candidate
        cand_map = {str(u.id): u for u in candidate_users}
        retrieved: list[tuple[User, UserProfileDict, float]] = []

        # 3. Thử tìm kiếm ngữ nghĩa qua Qdrant nếu có embedding
        qdrant_matched_ids: dict[str, float] = {}
        if query_embedding:
            try:
                results = self._vector_store.search_profiles(
                    query_embedding=query_embedding,
                    top_k=top_k,
                    exclude_user_ids=[current_profile["user_id"]],
                )
                for res in results:
                    uid = res.get("user_id")
                    if uid and uid in cand_map:
                        score = float(res.get("score", 0.5))
                        qdrant_matched_ids[uid] = max(0.0, min(1.0, score))
            except Exception as e:
                logger.warning(f"Vector search retrieval failed: {e}")

        # 4. Thu thập hồ sơ cho các ứng viên
        for cand in candidate_users:
            cand_id_str = str(cand.id)
            cand_profile = self.extract_user_profile(cand, db)
            
            # Semantic score từ Qdrant hoặc tính fallback
            semantic_score = qdrant_matched_ids.get(cand_id_str)
            if semantic_score is None:
                if query_embedding:
                    try:
                        cand_text = self.build_profile_text(cand_profile)
                        cand_emb = self._llm.embed(cand_text)
                        semantic_score = _cosine_similarity(query_embedding, cand_emb)
                        # Đồng thời upsert vào Qdrant để tối ưu cho các lần sau
                        self._vector_store.upsert_profile(
                            user_id=cand_id_str,
                            text=cand_text,
                            embedding=cand_emb,
                        )
                    except Exception:
                        semantic_score = 0.5
                else:
                    semantic_score = 0.5

            retrieved.append((cand, cand_profile, semantic_score))

        # Sắp xếp sơ bộ theo semantic similarity và lấy Top-K
        retrieved.sort(key=lambda item: item[2], reverse=True)
        return retrieved[:top_k]

    # =========================================================================
    # BƯỚC 3: Feature Engineering
    # =========================================================================
    def calculate_feature_scores(
        self,
        current_profile: UserProfileDict,
        candidate_profile: UserProfileDict,
        candidate_user: User,
        semantic_score: float = 0.5,
    ) -> FeatureScores:
        """
        Bước 3: Feature Engineering.
        Tính 6 đặc trưng chuẩn hóa trong khoảng [0.0, 1.0]:
        1. Semantic Similarity
        2. Skill Match
        3. Interest Match
        4. Goal / Looking-for Match (Mutual Synergy)
        5. Location Match
        6. Activity / Recency
        """
        # 1. Semantic Similarity
        s_semantic = max(0.0, min(1.0, float(semantic_score)))

        # 2. Skill Match (Jaccard similarity)
        s_skill = _calculate_jaccard(current_profile.get("skills", []), candidate_profile.get("skills", []))

        # 3. Interest Match (Jaccard similarity)
        s_interest = _calculate_jaccard(current_profile.get("interests", []), candidate_profile.get("interests", []))

        # 4. Goal / Looking-for Match (Synergy between Needs and Offers)
        s_goal = _calculate_goal_synergy(
            needs_a=current_profile.get("current_needs", []),
            offers_a=current_profile.get("current_offers", []),
            skills_a=current_profile.get("skills", []),
            needs_b=candidate_profile.get("current_needs", []),
            offers_b=candidate_profile.get("current_offers", []),
            skills_b=candidate_profile.get("skills", []),
        )

        # 5. Location Match
        s_location = _calculate_location_score(current_profile.get("location"), candidate_profile.get("location"))

        # 6. Activity / Recency
        s_activity = _calculate_activity_score(candidate_user)

        return FeatureScores(
            semantic=s_semantic,
            skill=s_skill,
            interest=s_interest,
            goal=s_goal,
            location=s_location,
            activity=s_activity,
        )

    # =========================================================================
    # BƯỚC 4: Weighted Scoring
    # =========================================================================
    def compute_weighted_score(self, features: FeatureScores) -> float:
        """
        Bước 4: Weighted Scoring.
        Score = 0.30 Semantic + 0.25 Skill + 0.15 Interest + 0.15 Goal + 0.10 Location + 0.05 Activity
        """
        raw_score = (
            0.30 * features.semantic
            + 0.25 * features.skill
            + 0.15 * features.interest
            + 0.15 * features.goal
            + 0.10 * features.location
            + 0.05 * features.activity
        )
        return round(max(0.0, min(1.0, raw_score)), 2)

    # =========================================================================
    # BƯỚC 5: Targeted LLM Refinement (Chỉ dùng Top 5)
    # =========================================================================
    async def compare_users(
        self,
        current_profile: UserProfileDict,
        candidate_profile: UserProfileDict,
        precomputed_score: float | None = None,
        features: FeatureScores | None = None,
    ) -> UserMatchResult | None:
        """
        Bước 5: Sử dụng LLM cho Top ứng viên để:
        - Kiểm tra ngữ cảnh chi tiết
        - Tạo lý do kết nối thuyết phục (reason)
        - Tạo câu mở lời chuyên nghiệp (suggested_intro)
        - Trích xuất điểm bổ trợ và sở thích chung
        """
        score = precomputed_score if precomputed_score is not None else 0.75
        score_percent = int(round(score * 100))

        priority = "HIGH" if score >= 0.8 else "MEDIUM" if score >= 0.6 else "LOW"

        # 1. Thử gọi LLM sinh lý do và câu chào hỏi
        prompt = GENERATE_MATCH_REASON_PROMPT.format(
            score_percent=score_percent,
            current_user_name=current_profile["full_name"],
            current_user_email=current_profile["email"],
            current_user_profession=current_profile.get("profession") or "Chưa cập nhật",
            current_user_company=current_profile.get("company") or "Chưa cập nhật",
            current_user_location=current_profile.get("location") or "Chưa cập nhật",
            current_user_skills=", ".join(current_profile.get("skills", [])) or "Chưa cập nhật",
            current_user_interests=", ".join(current_profile.get("interests", [])) or "Chưa cập nhật",
            current_user_needs=", ".join(current_profile.get("current_needs", [])) or "Chưa có nhu cầu cụ thể",
            current_user_offers=", ".join(current_profile.get("current_offers", [])) or "Chưa có chia sẻ cụ thể",
            candidate_name=candidate_profile["full_name"],
            candidate_email=candidate_profile["email"],
            candidate_profession=candidate_profile.get("profession") or "Chưa cập nhật",
            candidate_company=candidate_profile.get("company") or "Chưa cập nhật",
            candidate_location=candidate_profile.get("location") or "Chưa cập nhật",
            candidate_skills=", ".join(candidate_profile.get("skills", [])) or "Chưa cập nhật",
            candidate_interests=", ".join(candidate_profile.get("interests", [])) or "Chưa cập nhật",
            candidate_needs=", ".join(candidate_profile.get("current_needs", [])) or "Chưa có nhu cầu cụ thể",
            candidate_offers=", ".join(candidate_profile.get("current_offers", [])) or "Chưa có chia sẻ cụ thể",
        )

        try:
            response = self._llm.complete(prompt)
            parsed = self._parse_json_response(response)
            if parsed:
                llm_match_score = parsed.get("match_score")
                final_score = float(llm_match_score) if llm_match_score is not None else score
                final_score = round(max(0.0, min(1.0, final_score)), 2)

                final_priority = parsed.get("priority") or ("HIGH" if final_score >= 0.8 else "MEDIUM" if final_score >= 0.6 else "LOW")
                reason = parsed.get("reason")
                suggested_intro = parsed.get("suggested_intro")

                if reason and suggested_intro:
                    return UserMatchResult(
                        candidate_user_id=uuid.UUID(candidate_profile["user_id"]),
                        match_score=final_score,
                        priority=final_priority,
                        reason=reason,
                        suggested_intro=suggested_intro,
                        complementary_aspects=parsed.get("complementary_aspects", []),
                        shared_interests=parsed.get("shared_interests", []),
                        feature_scores=features,
                    )
        except Exception as e:
            logger.warning(f"LLM reason generation error for {current_profile['full_name']} vs {candidate_profile['full_name']}: {e}")

        # 2. Fallback Heuristic
        user_skills_preview = ", ".join(current_profile.get("skills", [])[:2]) or "công nghệ"
        cand_skills_preview = ", ".join(candidate_profile.get("skills", [])[:2]) or "chuyên môn"
        cand_company = candidate_profile.get("company") or "doanh nghiệp"
        cand_profession = candidate_profile.get("profession") or "chuyên gia"
        cand_loc = candidate_profile.get("location") or "Việt Nam"

        shared_interests = list(set([i.lower() for i in current_profile.get("interests", [])]) & set([i.lower() for i in candidate_profile.get("interests", [])]))

        reason = (
            f"Bạn nên kết nối với {candidate_profile['full_name']} ({cand_profession} tại {cand_company}, {cand_loc}) "
            f"vì có độ tương thích cao về kỹ năng ({cand_skills_preview}) và định hướng hợp tác."
        )
        suggested_intro = (
            f"Chào {candidate_profile['full_name']}, mình thấy bạn đang làm việc tại {cand_company} với chuyên môn về {cand_skills_preview}. "
            f"Mình rất muốn kết nối để trao đổi thêm cùng bạn!"
        )

        return UserMatchResult(
            candidate_user_id=uuid.UUID(candidate_profile["user_id"]),
            match_score=score,
            priority=priority,
            reason=reason,
            suggested_intro=suggested_intro,
            complementary_aspects=[f"Thế mạnh {cand_skills_preview}"],
            shared_interests=shared_interests,
            feature_scores=features,
        )

    # =========================================================================
    # PIPELINE CHÍNH: Generate Recommendations
    # =========================================================================
    async def generate(
        self,
        user_id: uuid.UUID,
        min_score: float = 0.4,
        limit: int = 5,
    ) -> list[Recommendation]:
        """
        Thực thi toàn bộ quy trình gợi ý kết nối 5 bước và lưu kết quả vào database:
        Bước 1: SQL Hard Filter
        Bước 2: Candidate Retrieval (Qdrant Vector Search -> Top 50)
        Bước 3: Feature Engineering (6 đặc trưng)
        Bước 4: Weighted Scoring (Chọn Top 5 ứng viên điểm cao nhất)
        Bước 5: Targeted LLM Refinement (Tạo Reason và Suggested Intro)
        """
        db = SessionLocal()
        try:
            current_user = db.get(User, user_id)
            if not current_user:
                logger.error(f"User {user_id} not found in database")
                return []

            if current_user.setting and not current_user.setting.ai_read_profile:
                logger.info(f"User {user_id} disabled profile reading. Skipping recommendation generation.")
                return []

            # 1. Trích xuất hồ sơ bản thân
            current_profile = self.extract_user_profile(current_user, db)

            # 2. Bước 1: SQL Hard Filter
            candidate_users = self.get_candidate_users(user_id, db)
            if not candidate_users:
                logger.info(f"No candidate users found for user {user_id} after SQL hard filter.")
                return []

            # 3. Bước 2: Candidate Retrieval (Qdrant Vector Search -> Top 50)
            retrieved_candidates = self.retrieve_candidates(
                current_profile=current_profile,
                candidate_users=candidate_users,
                db=db,
                top_k=50,
            )

            # 4. Bước 3 & Bước 4: Feature Engineering & Weighted Scoring
            scored_candidates: list[tuple[User, UserProfileDict, float, FeatureScores]] = []
            for cand_user, cand_prof, sem_score in retrieved_candidates:
                feat = self.calculate_feature_scores(
                    current_profile=current_profile,
                    candidate_profile=cand_prof,
                    candidate_user=cand_user,
                    semantic_score=sem_score,
                )
                comp_score = self.compute_weighted_score(feat)
                feat.composite_score = comp_score
                if comp_score >= min_score:
                    scored_candidates.append((cand_user, cand_prof, comp_score, feat))

            # Sắp xếp giảm dần theo điểm số tổng hợp
            scored_candidates.sort(key=lambda item: item[2], reverse=True)

            # Chọn đúng Top 5 (hoặc theo limit) ứng viên xuất sắc nhất để gửi vào LLM
            top_candidates = scored_candidates[:limit]

            # 5. Bước 5: Targeted LLM Refinement (Chỉ xử lý Top 5)
            final_matches: list[UserMatchResult] = []
            for cand_user, cand_prof, comp_score, feat in top_candidates:
                match = await self.compare_users(
                    current_profile=current_profile,
                    candidate_profile=cand_prof,
                    precomputed_score=comp_score,
                    features=feat,
                )
                if match and match.match_score >= min_score:
                    final_matches.append(match)

            # Sắp xếp kết quả cuối cùng theo match_score
            final_matches.sort(key=lambda m: m.match_score, reverse=True)

            # 6. Lưu kết quả vào bảng recommendations
            saved: list[Recommendation] = []
            for match in final_matches:
                rec = Recommendation(
                    owner_user_id=user_id,
                    target_user_id=match.candidate_user_id,
                    type="CONNECTION",
                    reason=match.reason,
                    priority=match.priority,
                    confidence=match.match_score,
                    status="PENDING",
                )
                db.add(rec)
                db.commit()
                db.refresh(rec)
                saved.append(rec)

            logger.info(f"Generated {len(saved)} high-quality connection recommendations for user {user_id}")
            return saved

        except Exception as e:
            db.rollback()
            logger.error(f"Error in ConnectionRecommendationAgent generate pipeline: {e}")
            raise
        finally:
            db.close()
