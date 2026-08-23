"""
Tagging Agent implementation for peer contact tagging.
"""

import json
import logging
import re
import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.agents.tagging.prompts import TAGGING_AGENT_PROMPT
from src.gateways.llm import LLMGateway
from src.models.ai import AssistantMemory
from src.models.chat import Conversation, Message
from src.models.user import User, UserProfile
from src.models.tag import AISystemConfig

logger = logging.getLogger(__name__)

# Danh sách từ rác/chung chung cần loại bỏ nếu LLM trả về
BLOCKED_TAGS = {
    "hôm nay", "chào", "chào bạn", "hello", "hi", "ok", "cảm ơn", "nói chuyện",
    "tin nhắn", "hẹn gặp", "rảnh rỗi", "giao tiếp", "người dùng", "chat", "unknown",
    "chưa rõ", "không rõ", "tự do", "ai", "null", "none", ""
}


class TaggingAgent:
    """
    Agent chuyên phân tích hội thoại và tự động gắn các tag quan trọng cho đối phương.
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

    def _clean_tags(self, raw_tags: list[str]) -> list[str]:
        """Lọc và chuẩn hóa danh sách tag."""
        cleaned = []
        seen = set()

        for tag in raw_tags:
            if not tag or not isinstance(tag, str):
                continue
            
            t = tag.strip().strip("#").strip()
            # Normalize casing: Capitalize first letter of each word
            t_norm = " ".join([word.capitalize() for word in t.split()])
            t_lower = t_norm.lower()

            if t_lower in BLOCKED_TAGS or len(t_norm) < 2 or len(t_norm) > 30:
                continue

            if t_lower not in seen:
                seen.add(t_lower)
                cleaned.append(t_norm)

        # Giới hạn tối đa 6 tags quan trọng nhất
        return cleaned[:6]

    def generate_tags(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        db: Session,
    ) -> list[str]:
        """
        Tự động phân tích hội thoại và sinh ra danh sách tag cho đối tác.
        """
        # Check global toggle
        current_user = db.get(User, user_id)
        if current_user and current_user.setting:
            if not current_user.setting.ai_enabled:
                return []

        # Get limit and features toggle
        ai_config = db.query(AISystemConfig).filter(
            AISystemConfig.user_id == user_id,
            AISystemConfig.key == "ai_settings"
        ).first()
        
        limit = 3
        if ai_config and isinstance(ai_config.value, dict):
            features = ai_config.value.get("features", {})
            # If tagging is explicitly disabled
            if features.get("tagging") is False:
                return []
            limit = int(ai_config.value.get("tag_limit", 3))

        conv = db.get(Conversation, conversation_id)
        if not conv:
            return []

        other_user_id = conv.user_b_id if str(conv.user_a_id) == str(user_id) else conv.user_a_id
        other_user = db.get(User, other_user_id)
        other_profile = db.query(UserProfile).filter(UserProfile.user_id == other_user_id).first()

        peer_name = other_user.full_name if other_user and other_user.full_name else (other_user.email if other_user else "Đối tác")
        peer_profession = other_profile.profession if other_profile and other_profile.profession else "Chưa rõ"
        peer_company = other_profile.company if other_profile and other_profile.company else "Chưa rõ"
        peer_location = other_profile.location if other_profile and other_profile.location else "Chưa rõ"

        # Lấy tin nhắn trong cuộc trò chuyện (tối đa 30 tin nhắn gần nhất)
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(30)
            .all()
        )
        messages.reverse()

        formatted_lines = []
        for msg in messages:
            sender_label = "[USER]" if str(msg.sender_user_id) == str(user_id) else "[PEER]"
            formatted_lines.append(f"{sender_label}: {msg.content}")

        conversation_text = "\n".join(formatted_lines) if formatted_lines else "Chưa có tin nhắn nào được trao đổi."

        # Nếu không có tin nhắn nhưng có profile đối tác, tạo tag ban đầu từ profile
        if not formatted_lines and other_profile:
            initial_tags = []
            if other_profile.profession:
                initial_tags.append(other_profile.profession)
            if other_profile.company:
                initial_tags.append(other_profile.company)
            if other_profile.skills:
                initial_tags.extend(other_profile.skills[:2])
            
            cleaned = self._clean_tags(initial_tags)[:limit]
            self._save_tags_to_memory(conversation_id, user_id, cleaned, db)
            return cleaned

        from src.models.tag import Tag
        user_tags = db.query(Tag).filter(Tag.user_id == user_id, Tag.is_active == True).all()
        existing_tags_str = ", ".join([t.name for t in user_tags]) if user_tags else "Chưa có"

        prompt = TAGGING_AGENT_PROMPT.format(
            conversation=conversation_text,
            peer_name=peer_name,
            peer_profession=peer_profession,
            peer_company=peer_company,
            peer_location=peer_location,
            existing_tags=existing_tags_str,
        )

        try:
            response = self._llm.complete(prompt)
            parsed = self._parse_json_response(response)
            if parsed and isinstance(parsed.get("tags"), list):
                tags = self._clean_tags(parsed["tags"])
            else:
                tags = []
        except Exception as e:
            logger.error(f"Error running TaggingAgent: {e}")
            tags = []

        # Nếu LLM không trả về tag nào mà peer có profile, fallback lấy từ profile
        if not tags and other_profile:
            fallback = []
            if other_profile.profession:
                fallback.append(other_profile.profession)
            if other_profile.company:
                fallback.append(other_profile.company)
            tags = self._clean_tags(fallback)

        # Map generated tags to existing tags' casing if they match, and keep new tags.
        if user_tags:
            valid_tag_names = {t.name.lower(): t.name for t in user_tags}
            final_tags = []
            for t in tags:
                if t.lower() in valid_tag_names:
                    final_tags.append(valid_tag_names[t.lower()])
                else:
                    final_tags.append(t)
            tags = final_tags

        tags = tags[:limit]
        self._save_tags_to_memory(conversation_id, user_id, tags, db)
        return tags

    def _save_tags_to_memory(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        tags: list[str],
        db: Session,
    ) -> None:
        """Lưu tags vào AssistantMemory của user cho conversation này."""
        memory = (
            db.query(AssistantMemory)
            .filter(
                AssistantMemory.owner_user_id == user_id,
                AssistantMemory.conversation_id == conversation_id,
            )
            .first()
        )

        if not memory:
            memory = AssistantMemory(
                owner_user_id=user_id,
                conversation_id=conversation_id,
                facts={"pending_tags": tags, "tags": []},
                summary="",
            )
            db.add(memory)
        else:
            facts = dict(memory.facts or {})
            existing_tags = facts.get("tags", [])
            pending_tags = facts.get("pending_tags", [])
            for t in tags:
                if t not in existing_tags and t not in pending_tags:
                    pending_tags.append(t)
            facts["pending_tags"] = pending_tags
            if "tags" not in facts:
                facts["tags"] = existing_tags
            memory.facts = facts

        db.commit()
        db.refresh(memory)
