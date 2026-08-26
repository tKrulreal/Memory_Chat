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
        QUY TẮC: CHỈ được chọn từ các tag mà người dùng đã định nghĩa trước trong AI Hub.
        Nếu người dùng chưa định nghĩa tag nào trong AI Hub, trả về [] (không tự ý bịa tag).
        """
        # 1. Check global toggle
        current_user = db.get(User, user_id)
        if current_user and current_user.setting:
            if not current_user.setting.ai_enabled:
                return []

        # 2. Query active tags configured by user in AI Hub
        from src.models.tag import Tag, AISystemConfig
        user_tags = db.query(Tag).filter(Tag.user_id == user_id, Tag.is_active == True).all()
        if not user_tags:
            logger.info("User %s has not configured any tags in AI Hub. Skipping tagging.", user_id)
            self._save_tags_to_memory(conversation_id, user_id, [], db)
            return []

        # Find existing attached tags for this contact
        memory = (
            db.query(AssistantMemory)
            .filter(
                AssistantMemory.owner_user_id == user_id,
                AssistantMemory.conversation_id == conversation_id,
            )
            .first()
        )
        existing_facts = dict(memory.facts or {}) if memory else {}
        already_attached = list(existing_facts.get("tags", []))

        # Filter available tags from AI Hub that are not yet attached
        available_user_tags = [t for t in user_tags if t.name not in already_attached]
        if not available_user_tags:
            logger.info("All user AI Hub tags are already attached for peer %s.", conversation_id)
            self._save_tags_to_memory(conversation_id, user_id, [], db)
            return []

        # Map for fast and case-insensitive lookup
        valid_tag_map = {t.name.lower().strip(): t.name for t in available_user_tags}
        available_tags_str = ", ".join([t.name for t in available_user_tags])
        already_attached_str = ", ".join(already_attached) if already_attached else "Chưa có"

        # 3. Get limit and features toggle
        ai_config = db.query(AISystemConfig).filter(
            AISystemConfig.user_id == user_id,
            AISystemConfig.key == "ai_settings"
        ).first()
        
        limit = 3
        if ai_config and isinstance(ai_config.value, dict):
            features = ai_config.value.get("features", {})
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

        prompt = TAGGING_AGENT_PROMPT.format(
            conversation=conversation_text,
            peer_name=peer_name,
            peer_profession=peer_profession,
            peer_company=peer_company,
            peer_location=peer_location,
            already_attached_tags=already_attached_str,
            available_tags=available_tags_str,
        )

        try:
            response = self._llm.complete(prompt)
            parsed = self._parse_json_response(response)
            if parsed and isinstance(parsed.get("tags"), list):
                raw_tags = parsed["tags"]
            else:
                raw_tags = []
        except Exception as e:
            logger.error(f"Error running TaggingAgent: {e}")
            raw_tags = []

        # STRICT FILTERING: Only accept tags that match available user's AI Hub tags
        final_tags = []
        for t in raw_tags:
            if not isinstance(t, str):
                continue
            t_norm = t.strip().strip("#").lower()
            if t_norm in valid_tag_map:
                canonical_name = valid_tag_map[t_norm]
                if canonical_name not in final_tags and canonical_name not in already_attached:
                    final_tags.append(canonical_name)

        final_tags = final_tags[:limit]
        self._save_tags_to_memory(conversation_id, user_id, final_tags, db)
        return final_tags

    def _save_tags_to_memory(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        tags: list[str],
        db: Session,
    ) -> None:
        """Lưu pending_tags vào AssistantMemory của user cho conversation này."""
        memory = (
            db.query(AssistantMemory)
            .filter(
                AssistantMemory.owner_user_id == user_id,
                AssistantMemory.conversation_id == conversation_id,
            )
            .first()
        )

        from sqlalchemy.orm.attributes import flag_modified

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
            existing_tags = list(facts.get("tags", []))
            # Pending tags are the new suggestions that are not already attached
            new_pending = [t for t in tags if t not in existing_tags]
            facts["pending_tags"] = new_pending
            facts["tags"] = existing_tags
            memory.facts = facts
            flag_modified(memory, "facts")

        db.commit()
        db.refresh(memory)
