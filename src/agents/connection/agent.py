"""
Connection Recommendation Agent (User-to-User Networking).

Tự động trích xuất các trường thông tin then chốt (Company, Location, Skills, Interests, Looking for, Offering)
và sử dụng AI LLM để đánh giá sự phù hợp kết nối giữa các người dùng thật.
"""

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from src.agents.connection.prompts import (
    ANALYZE_USER_PROFILE_PROMPT,
    COMPARE_USERS_PROMPT,
)
from src.agents.connection.schemas import (
    UserProfileDict,
    ConnectionRecommendation as ConnectionRecommendationSchema,
    ConnectionRecommendationDetail,
)
from src.gateways.llm import LLMGateway
from src.models.database import SessionLocal
from src.models.user import User, UserProfile
from src.models.ai import AssistantMemory, Recommendation

from src.models.chat import Conversation, Message
from src.models.contact import Contact

logger = logging.getLogger(__name__)


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


class ConnectionRecommendationAgent:
    """
    Agent trích xuất hồ sơ chọn lọc và so khớp mức độ tương thích bằng AI.
    """

    def __init__(self, llm: LLMGateway | None = None):
        self._llm = llm or LLMGateway()

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
        1. Ưu tiên 1 (Cao nhất): Dữ liệu do chính người dùng tự nhập trong bảng UserProfile (Company, Location, Profession, Skills, Interests, Looking for, Offering, Bio).
        2. Ưu tiên 2 (Tự động trích xuất): Nếu người dùng chưa nhập trường nào, trích xuất tự động từ lịch sử hội thoại (AssistantMemory & Messages).
        """
        collected_skills: list[str] = []
        collected_interests: list[str] = []
        collected_needs: list[str] = []
        collected_offers: list[str] = []
        profession: str | None = None
        company: str | None = None
        location: str | None = None

        # 1. Ưu tiên 1: Đọc dữ liệu do chính người dùng tự nhập (UserProfile)
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

        # 2. Ưu tiên 2: Trích xuất từ Assistant Memories nếu các trường chưa được người dùng tự nhập
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
                if not profession and "profession" in m.facts and m.facts["profession"]:
                    profession = str(m.facts["profession"])
                if not company and "company" in m.facts and m.facts["company"]:
                    company = str(m.facts["company"])
                if not location and "location" in m.facts and m.facts["location"]:
                    location = str(m.facts["location"])
                if not collected_skills and "skills" in m.facts and isinstance(m.facts["skills"], list):
                    collected_skills.extend([str(s) for s in m.facts["skills"]])
                if not collected_interests and "interested_in" in m.facts and isinstance(m.facts["interested_in"], list):
                    collected_interests.extend([str(i) for i in m.facts["interested_in"]])
                if not collected_interests and "interests" in m.facts and isinstance(m.facts["interests"], list):
                    collected_interests.extend([str(i) for i in m.facts["interests"]])
                if not collected_needs and "looking_for" in m.facts and isinstance(m.facts["looking_for"], list):
                    collected_needs.extend([str(n) for n in m.facts["looking_for"]])
                if not collected_needs and "current_needs" in m.facts and isinstance(m.facts["current_needs"], list):
                    collected_needs.extend([str(n) for n in m.facts["current_needs"]])
                if not collected_offers and "offering" in m.facts and isinstance(m.facts["offering"], list):
                    collected_offers.extend([str(o) for o in m.facts["offering"]])
                if not collected_offers and "current_offers" in m.facts and isinstance(m.facts["current_offers"], list):
                    collected_offers.extend([str(o) for o in m.facts["current_offers"]])

        # 3. Lấy tin nhắn do chính người dùng này gửi đi trong các hội thoại để phân tích
        recent_msgs = (
            db.query(Message)
            .filter(Message.sender_user_id == user.id)
            .order_by(Message.created_at.desc())
            .limit(20)
            .all()
        )
        recent_messages_text = "\n".join([f"- {msg.content}" for msg in recent_msgs if msg.content and msg.content.strip()]) or "Chưa gửi tin nhắn nào"

        # 4. Kiểm tra xem có Contact record do chính user tự tạo không (nếu vẫn chưa có)
        if not profession or not company:
            contact_record = (
                db.query(Contact)
                .filter(Contact.owner_user_id == user.id)
                .first()
            )
            if contact_record:
                profession = profession or contact_record.profession
                company = company or contact_record.company

        # 5. Nếu người dùng CHƯA nhập và danh sách kỹ năng/chuyên môn còn trống, dùng LLM phân tích từ tin nhắn do chính họ gửi
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
            summary=memories_summary if memories_summary != "Chưa có hội thoại trợ lý" else None,
        )


    def get_candidate_users(self, user_id: uuid.UUID, db: Session) -> list[User]:
        """
        Lấy danh sách các người dùng thật khác trong database chưa từng kết nối với user hiện tại.
        """
        # 1. Tìm các user đã có Direct Conversation với user_id
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
        connected_user_ids = set()
        for c in existing_convs:
            connected_user_ids.add(c.user_a_id)
            connected_user_ids.add(c.user_b_id)

        # 2. Tìm các user đã có Recommendation PENDING
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
                connected_user_ids.add(r.target_user_id)

        # 3. Lấy tất cả user khác chưa có trong danh sách trên
        candidates = (
            db.query(User)
            .filter(
                User.id != user_id,
                ~User.id.in_(connected_user_ids) if connected_user_ids else True,
            )
            .all()
        )
        return candidates

    async def compare_users(
        self,
        current_profile: UserProfileDict,
        candidate_profile: UserProfileDict,
    ) -> UserMatchResult | None:
        """
        Sử dụng AI LLM để đánh giá độ tương thích giữa 2 hồ sơ định dạng chuẩn.
        """
        prompt = COMPARE_USERS_PROMPT.format(
            current_user_name=current_profile["full_name"],
            current_user_email=current_profile["email"],
            current_user_profession=current_profile.get("profession") or "Chưa cập nhật",
            current_user_company=current_profile.get("company") or "Chưa cập nhật",
            current_user_location=current_profile.get("location") or "Chưa cập nhật",
            current_user_skills_bullet=self._format_bullets(current_profile["skills"], default_text="Chưa chia sẻ trong hội thoại"),
            current_user_interests_bullet=self._format_bullets(current_profile["interests"], default_text="Chưa chia sẻ trong hội thoại"),
            current_user_needs_bullet=self._format_bullets(current_profile["current_needs"], default_text="Chưa có nhu cầu cụ thể"),
            current_user_offers_bullet=self._format_bullets(current_profile["current_offers"], default_text="Chưa có thông tin chia sẻ"),
            candidate_name=candidate_profile["full_name"],
            candidate_email=candidate_profile["email"],
            candidate_profession=candidate_profile.get("profession") or "Chưa cập nhật",
            candidate_company=candidate_profile.get("company") or "Chưa cập nhật",
            candidate_location=candidate_profile.get("location") or "Chưa cập nhật",
            candidate_skills_bullet=self._format_bullets(candidate_profile["skills"], default_text="Chưa chia sẻ trong hội thoại"),
            candidate_interests_bullet=self._format_bullets(candidate_profile["interests"], default_text="Chưa chia sẻ trong hội thoại"),
            candidate_needs_bullet=self._format_bullets(candidate_profile["current_needs"], default_text="Chưa có nhu cầu cụ thể"),
            candidate_offers_bullet=self._format_bullets(candidate_profile["current_offers"], default_text="Chưa có thông tin chia sẻ"),
        )


        try:
            response = self._llm.complete(prompt)
            parsed = self._parse_json_response(response)
            if parsed and "match_score" in parsed:
                raw_score = float(parsed.get("match_score", 0.0))
                # Normalize and round to 2 decimal places (e.g. 0.94, 0.88, 0.73)
                score = round(min(1.0, max(0.0, raw_score)), 2)

                priority = parsed.get("priority", "MEDIUM")
                if score >= 0.8:
                    priority = "HIGH"
                elif score < 0.6:
                    priority = "LOW"
                else:
                    priority = "MEDIUM"

                reason = parsed.get(
                    "reason",
                    f"Bạn nên kết nối với {candidate_profile['full_name']} ({candidate_profile['profession']} tại {candidate_profile['company']}) vì có nhiều điểm tương đồng về chuyên môn và định hướng hợp tác.",
                )
                suggested_intro = parsed.get(
                    "suggested_intro",
                    f"Chào {candidate_profile['full_name']}, mình thấy bạn đang làm việc tại {candidate_profile['company']} với chuyên môn về {', '.join(candidate_profile['skills'][:2])}. Rất vui được kết nối cùng bạn!",
                )

                return UserMatchResult(
                    candidate_user_id=uuid.UUID(candidate_profile["user_id"]),
                    match_score=score,
                    priority=priority,
                    reason=reason,
                    suggested_intro=suggested_intro,
                    complementary_aspects=parsed.get("complementary_aspects", []),
                    shared_interests=parsed.get("shared_interests", []),
                )
        except Exception as e:
            logger.warning(f"LLM comparison error for {current_profile['full_name']} vs {candidate_profile['full_name']}: {e}")

        # Dynamic fallback
        user_tokens = set([t.lower() for t in (current_profile["skills"] + current_profile["interests"] + current_profile["current_needs"])])
        cand_tokens = set([t.lower() for t in (candidate_profile["skills"] + candidate_profile["interests"] + candidate_profile["current_offers"])])
        shared_tokens = user_tokens & cand_tokens
        total_tokens = user_tokens | cand_tokens
        jaccard_ratio = (len(shared_tokens) / len(total_tokens)) if total_tokens else 0.0

        calculated_score = round(min(0.95, max(0.50, 0.55 + jaccard_ratio * 0.8)), 2)
        priority = "HIGH" if calculated_score >= 0.8 else "MEDIUM" if calculated_score >= 0.6 else "LOW"

        cand_loc = candidate_profile.get("location") or "Việt Nam"
        return UserMatchResult(
            candidate_user_id=uuid.UUID(candidate_profile["user_id"]),
            match_score=calculated_score,
            priority=priority,
            reason=f"Bạn nên kết nối với {candidate_profile['full_name']} ({candidate_profile['profession']} tại {candidate_profile['company']}, {cand_loc}) vì bạn đang quan tâm đến {', '.join(current_profile['interests'][:2])}, trong khi {candidate_profile['full_name']} có thế mạnh về {', '.join(candidate_profile['skills'][:2])}.",
            suggested_intro=f"Chào {candidate_profile['full_name']}, mình thấy bạn đang làm việc tại {candidate_profile['company']}. Mình rất muốn kết nối để trao đổi thêm cùng bạn!",
            shared_interests=list(shared_tokens),
        )

    async def generate(
        self,
        user_id: uuid.UUID,
        min_score: float = 0.5,
        limit: int = 5,
    ) -> list[Recommendation]:
        """
        Tìm kiếm các người dùng thật trong DB và tạo gợi ý kết nối cho user_id bằng AI thật.
        """
        db = SessionLocal()
        try:
            current_user = db.get(User, user_id)
            if not current_user:
                logger.error(f"User {user_id} not found in database")
                return []

            # 1. Extract current user profile from DB
            current_profile = self.extract_user_profile(current_user, db)

            # 2. Get candidate real users
            candidate_users = self.get_candidate_users(user_id, db)
            if not candidate_users:
                logger.info(f"No new candidate users found for user {user_id}")
                return []

            # 3. Compare each candidate with current user using AI LLM
            matches: list[UserMatchResult] = []
            for candidate in candidate_users:
                candidate_profile = self.extract_user_profile(candidate, db)
                match = await self.compare_users(current_profile, candidate_profile)
                if match and match.match_score >= min_score:
                    matches.append(match)

            # 4. Sort by score descending and limit
            matches.sort(key=lambda m: m.match_score, reverse=True)
            top_matches = matches[:limit]

            # 5. Save recommendations to database
            saved: list[Recommendation] = []
            for match in top_matches:
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

            logger.info(f"Generated {len(saved)} real user connection recommendations for {current_user.email}")
            return saved

        except Exception as e:
            db.rollback()
            logger.error(f"Error generating real user recommendations: {e}")
            raise
        finally:
            db.close()
