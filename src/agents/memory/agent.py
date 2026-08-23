"""
Memory Agent — biến hội thoại thành tri thức.

Responsibilities:
- Tóm tắt conversation (summarize)
- Trích xuất entities (company, profession, skills, interests)
- Tính relationship_score (rule-based)
- Tổng hợp thành ContactMemory
"""

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.gateways.llm import LLMGateway

logger = logging.getLogger(__name__)

# --- Token estimation (no tiktoken dependency) ---
AVG_CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Ước tính số tokens trong text."""
    return len(text) // AVG_CHARS_PER_TOKEN


def chunk_messages(messages: list[dict[str, Any]], max_tokens: int = 500) -> list[list[dict[str, Any]]]:
    """
    Chia messages thành chunks, mỗi chunk <= max_tokens.

    Args:
        messages: List of {content, sender_type, created_at}
        max_tokens: Số tokens tối đa mỗi chunk

    Returns:
        List of chunks
    """
    chunks: list[list[dict[str, Any]]] = []
    current_chunk: list[dict[str, Any]] = []
    current_tokens = 0

    for msg in messages:
        msg_tokens = estimate_tokens(msg.get("content", ""))
        if current_tokens + msg_tokens > max_tokens and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0
        current_chunk.append(msg)
        current_tokens += msg_tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def format_conversation_for_prompt(messages: list[dict[str, Any]], owner_id: str = "") -> str:
    """Format messages thành text để đưa vào prompt."""
    lines = []
    for msg in messages:
        sender_id = msg.get("sender_user_id", "")
        if sender_id and owner_id:
            sender = "USER" if sender_id == str(owner_id) else "PEER"
        else:
            sender = msg.get("sender_type", "UNKNOWN").upper()
            
        content = msg.get("content", "")
        time_str = ""
        if msg.get("created_at"):
            try:
                dt = msg["created_at"]
                if isinstance(dt, datetime):
                    time_str = dt.strftime("%d/%m/%Y")
                else:
                    time_str = str(dt)[:10]
            except Exception:
                pass
        lines.append(f"[{sender}]{time_str}: {content}")
    return "\n".join(lines)


# --- Memory Result dataclass ---
@dataclass
class MemoryResult:
    """Kết quả từ Memory Agent."""

    summary: str
    last_met: str | None = None
    interested_in: list[str] = field(default_factory=list)
    follow_up: str | None = None
    timeline: list[dict[str, Any]] = field(default_factory=list)
    relationship_score: int = 50  # 0-100
    timeline: list[dict[str, Any]] = field(default_factory=list)
    relationship_score: int = 50  # 0-100

    def to_contact_memory_dict(self, contact_id: uuid.UUID) -> dict[str, Any]:
        """Convert sang dict để lưu vào ContactMemory."""
        return {
            "contact_id": contact_id,
            "summary": self.summary,
            "last_met": self.last_met,
            "interested_in": {"interests": self.interested_in},
            "follow_up": self.follow_up,
            "timeline": {"events": self.timeline},
            "relationship_score": self.relationship_score,
        }


# --- Prompt templates ---
MEMORY_SUMMARY_PROMPT = """Bạn là một AI assistant chuyên phân tích hội thoại để tạo tóm tắt trí nhớ súc tích, trực quan về NGƯỜI ĐỐI THOẠI.

Hội thoại:
{conversation}

Chú thích:
- [USER] là người dùng hiện tại (chủ sở hữu trí nhớ này).
- [PEER] là đối tác/người đang nhắn tin cùng.

{system_rules}

QUY TẮC BẮT BUỘC:
1. CHỈ tóm tắt thông tin về ĐỐI TÁC ĐANG TRÒ CHUYỆN dựa trên những gì họ trực tiếp nói hoặc thể hiện.
2. TUYỆT ĐỐI KHÔNG đưa thông tin, kỹ năng, quan điểm hoặc công việc của [USER] vào bản tóm tắt này.
3. TUYỆT ĐỐI KHÔNG xuất hiện các từ kỹ thuật như `[PEER]`, `[USER]`, `PEER:`, `USER:` trong văn bản tóm tắt. Hãy sử dụng danh xưng tự nhiên như "Đối tác", "Anh/Chị", "Bạn này" hoặc đại từ phù hợp.
4. Tóm tắt trực quan, ngắn gọn, súc tích (1 đến 2 câu ngắn, tối đa 3 câu). Không lan man dài dòng.
5. Không bịa đặt thông tin nếu đối phương không nhắc đến. Bỏ qua các câu chào hỏi xã giao vụn vặt.

Nội dung trọng tâm:
- Nghề nghiệp / Công ty / Nơi làm việc của đối phương (nếu có nhắc đến).
- Chủ đề chuyên môn, kỹ năng chính hoặc nhu cầu trao đổi nổi bật của đối phương.

Trả lời CHỈ bằng 1 đoạn tóm tắt tiếng Việt ngắn gọn, không giải thích thêm.
"""

MEMORY_ENTITIES_PROMPT = """Bạn là một AI assistant chuyên trích xuất thông tin cá nhân và chuyên môn từ hội thoại.

Hội thoại:
{conversation}

Chú thích:
- [USER] là người dùng hiện tại.
- [PEER] là đối tác/người đang nhắn tin cùng.

{system_rules}

QUY TẮC BẮT BUỘC:
1. CHỈ trích xuất thông tin về ĐỐI TÁC ([PEER]). TUYỆT ĐỐI KHÔNG trích xuất thông tin của [USER].
2. TUYỆT ĐỐI KHÔNG để xuất hiện các từ `[PEER]`, `[USER]` trong các giá trị trích xuất.
3. QUY TẮC CHO "interested_in" (ĐẶC BIỆT QUAN TRỌNG):
   - CHỈ trích xuất từ 2 đến 5 từ khóa / chủ đề CHÍNH, ngắn gọn, súc tích (1 - 3 từ mỗi mục).
   - Ví dụ đúng: "AI", "LLM", "Robot", "Đá bóng", "Startup", "Tài chính", "Du lịch", "Thiết kế".
   - TUYỆT ĐỐI KHÔNG viết câu dài, mệnh đề giải thích lê thê (CẤM: "tìm hiểu về mô hình ngôn ngữ lớn để áp dụng vào doanh nghiệp").
4. "last_met": Bối cảnh quen biết, thời điểm hoặc sự kiện gặp gỡ gần nhất (ngắn gọn, hoặc null nếu không có).
5. "follow_up": 1 câu ngắn gọn gợi ý hành động/chủ đề tiếp theo nên trao đổi (hoặc null nếu không có).
6. Không bịa đặt (hallucinate). Nếu không có thông tin thì để null hoặc [].

Hãy trích xuất thông tin của đối tác (chỉ trả về JSON):
{{
    "last_met": "Bối cảnh quen biết hoặc lần gặp gần nhất (hoặc null)",
    "interested_in": ["AI", "LLM", "Robot", "Đá bóng"],
    "follow_up": "Chủ đề tiếp theo nên trao đổi (hoặc null)"
}}

Trả lời CHỈ bằng JSON, không giải thích thêm.
"""


def sanitize_peer_text(text: str | None) -> str | None:
    """Làm sạch văn bản, loại bỏ triệt để các token rò rỉ như [PEER], {peer}, [USER]."""
    if not text:
        return text
    cleaned = re.sub(r"\[PEER\]|\{peer\}|\[peer\]|\bPEER\b", "Đối tác", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"\[USER\]|\{user\}|\[user\]|\bUSER\b", "Bạn", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def clean_interest_keyword(item: str | None) -> str | None:
    """Chuẩn hóa chủ đề quan tâm thành từ khóa ngắn gọn (1-3 từ)."""
    if not item:
        return None
    cleaned = sanitize_peer_text(str(item).strip().strip("#").strip())
    if not cleaned:
        return None
    words = cleaned.split()
    if len(words) > 4:
        cleaned = " ".join(words[:3])
    # Capitalize first letter of each word
    return " ".join(w.capitalize() for w in cleaned.split())



class MemoryAgent:
    """
    Memory Agent — phân tích conversation và sinh ContactMemory.

    Usage:
        agent = MemoryAgent()
        result = await agent.build_memory(contact_id, messages)
    """

    def __init__(self, llm: LLMGateway | None = None):
        self._llm = llm or LLMGateway()

    async def summarize(self, messages: list[dict[str, Any]], owner_id: str = "", system_rules: str = "") -> str:
        """
        Tóm tắt conversation.

        Args:
            messages: List of {content, sender_type, created_at}

        Returns:
            Summary string
        """
        if not messages:
            return "Chưa có đủ trao đổi để tóm tắt."

        # Chunk nếu quá dài
        chunks = chunk_messages(messages, max_tokens=500)
        summaries = []

        for i, chunk in enumerate(chunks):
            text = format_conversation_for_prompt(chunk, owner_id=owner_id)
            prompt = MEMORY_SUMMARY_PROMPT.format(conversation=text, system_rules=system_rules)
            try:
                summary = self._llm.complete(prompt)
                cleaned = sanitize_peer_text(summary.strip())
                if cleaned:
                    summaries.append(cleaned)
            except Exception as e:
                logger.warning("LLM summarize failed for chunk %d: %s", i, e)
                summaries.append("") 
                
        if len(summaries) == 1:
            return summaries[0]

        # Nếu có nhiều chunks, tóm tắt lại
        combined = " ".join(s for s in summaries if s)
        if not combined:
            return "Chưa có đủ thông tin để tóm tắt."

        final_prompt = (
            f"Bạn hãy tóm tắt ngắn gọn các ý sau thành 1-2 câu mô tả súc tích về người đối thoại:\n{combined}\n\n"
            f"Tuyệt đối KHÔNG viết từ '[PEER]' hay '[USER]', chỉ dùng văn phong tiếng Việt tự nhiên."
        )
        try:
            res = self._llm.complete(final_prompt).strip()
            return sanitize_peer_text(res) or res
        except Exception as e:
            logger.warning("LLM final summarize failed: %s", e)
            return sanitize_peer_text(combined[:200]) or combined[:200]


    async def extract_entities(self, messages: list[dict[str, Any]], owner_id: str = "", system_rules: str = "") -> dict[str, Any]:
        """
        Trích xuất entities từ conversation.

        Args:
            messages: List of {content, sender_type, created_at}

        Returns:
            Dict với keys: last_met, interested_in, follow_up
        """
        if not messages:
            return {"last_met": None, "interested_in": [], "follow_up": None}

        chunks = chunk_messages(messages, max_tokens=500)
        all_results: list[dict[str, Any]] = []

        for i, chunk in enumerate(chunks):
            text = format_conversation_for_prompt(chunk, owner_id=owner_id)
            prompt = MEMORY_ENTITIES_PROMPT.format(conversation=text, system_rules=system_rules)
            try:
                raw = self._llm.complete(prompt)
                # Parse JSON response
                parsed = self._parse_json_response(raw)
                if parsed:
                    all_results.append(parsed)
            except Exception as e:
                logger.warning("LLM extract_entities failed for chunk %d: %s", i, e)

        # Merge results
        return self._merge_entity_results(all_results)

    def _parse_json_response(self, raw: str) -> dict[str, Any] | None:
        """Parse JSON từ LLM response."""
        # Try direct JSON
        try:
            return json.loads(raw)
        except Exception:
            pass

        # Try extract from markdown code block
        match = re.search(r"```(?:json)?\s*([\s\S]+?)```", raw)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except Exception:
                pass

        # Try find JSON-like structure
        match = re.search(r"\{[\s\S]+\}", raw)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass

        return None

    def _merge_entity_results(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Merge nhiều entity results thành 1."""
        if not results:
            return {"last_met": None, "interested_in": [], "follow_up": None}
        if len(results) == 1:
            r = results[0]
            raw_interests = r.get("interested_in", [])
            interests = [clean_interest_keyword(i) for i in raw_interests if i]
            return {
                "last_met": sanitize_peer_text(r.get("last_met")),
                "interested_in": [i for i in interests if i][:6],
                "follow_up": sanitize_peer_text(r.get("follow_up")),
            }

        # Collect from all
        last_mets = [sanitize_peer_text(r["last_met"]) for r in results if r.get("last_met")]
        follow_ups = [sanitize_peer_text(r["follow_up"]) for r in results if r.get("follow_up")]
        all_interests: list[str] = []
        seen_interests: set[str] = set()

        for r in results:
            interests = r.get("interested_in") or []
            for interest in interests:
                cleaned = clean_interest_keyword(interest)
                norm = cleaned.lower() if cleaned else ""
                if norm and norm not in seen_interests:
                    seen_interests.add(norm)
                    all_interests.append(cleaned)

        return {
            "last_met": last_mets[0] if last_mets else None,
            "interested_in": all_interests[:6],
            "follow_up": follow_ups[0] if follow_ups else None,
        }


    def calculate_relationship_score(self, messages: list[dict[str, Any]]) -> int:
        """
        Tính relationship score (0-100) dựa trên rule-based heuristics.

        Args:
            messages: List of {content, sender_type, created_at}

        Returns:
            Score 0-100
        """
        if not messages:
            return 0

        # Base score from message count
        count = len(messages)
        score = min(30, count * 3)  # max 30 pts from count

        # Check conversation length
        total_chars = sum(len(m.get("content", "")) for m in messages)
        if total_chars > 5000:
            score += 20
        elif total_chars > 1000:
            score += 10
        else:
            score += 5

        # Recent conversation bonus (within 7 days)
        try:
            first_msg = messages[0].get("created_at")
            last_msg = messages[-1].get("created_at")
            if first_msg and last_msg:
                if isinstance(first_msg, datetime) and isinstance(last_msg, datetime):
                    days_diff = (last_msg - first_msg).days
                    if days_diff <= 7:
                        score += 10
        except Exception:
            pass

        # Variety bonus (both USER and CONTACT messages)
        sender_types = {m.get("sender_type") for m in messages}
        if len(sender_types) >= 2:
            score += 10

        # Positive language indicators
        positive_words = [
            "cảm ơn", "thanks", "thank", "được", "ok", "okay",
            "hay", "tốt", "tuyệt", "vui", "happy", "nice",
            "đồng ý", "agree", "perfect", "awesome", "👍",
        ]
        all_text = " ".join(m.get("content", "").lower() for m in messages)
        positive_count = sum(1 for w in positive_words if w in all_text)
        score += min(15, positive_count * 3)

        # Formal language (might indicate professional relationship)
        formal_words = ["em", "anh", "chị", "bạn", "thầy", "cô"]
        informal_count = sum(1 for w in formal_words if w in all_text)
        if informal_count > 0:
            score += 5

        # Cap at 100
        return min(100, max(0, score))

    def build_timeline(
        self, messages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Tạo timeline từ messages.

        Args:
            messages: List of {content, sender_type, created_at}

        Returns:
            List of {date, summary, sender_type}
        """
        if not messages:
            return []

        timeline: list[dict[str, Any]] = []
        date_buckets: dict[str, list[dict[str, Any]]] = {}

        for msg in messages:
            created_at = msg.get("created_at")
            if not created_at:
                continue
            try:
                if isinstance(created_at, datetime):
                    date_key = created_at.strftime("%Y-%m-%d")
                else:
                    date_key = str(created_at)[:10]
            except Exception:
                date_key = "unknown"

            date_buckets.setdefault(date_key, []).append(msg)

        # Create summary per date
        for date_key in sorted(date_buckets.keys()):
            msgs = date_buckets[date_key]
            content_preview = msgs[-1].get("content", "")[:100] if msgs else ""
            senders = {m.get("sender_type") for m in msgs}
            timeline.append({
                "date": date_key,
                "message_count": len(msgs),
                "last_message_preview": content_preview,
                "participants": list(senders),
            })

        return timeline[-10:]  # Last 10 dates

    async def build_memory(
        self,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        messages: list[dict[str, Any]],
        db: Any = None,
    ) -> MemoryResult:
        """
        Tổng hợp — gọi tất cả methods và trả về MemoryResult.
        """
        logger.info("Building memory for conversation_id=%s, owner=%s with %d messages", conversation_id, user_id, len(messages))

        system_rules = ""
        memory_window_days = None
        if db:
            from src.models.tag import AISystemConfig
            configs = db.query(AISystemConfig).all()
            rules = []
            for c in configs:
                rules.append(f"- {c.key}: {c.value}")
            if rules:
                system_rules = "Quy tắc hệ thống (TỪ AI_SYSTEM_CONFIG):\n" + "\n".join(rules) + "\n"
                
            from src.models.user import Setting
            setting = db.query(Setting).filter(Setting.user_id == user_id).first()
            if setting and setting.ai_memory_window and str(setting.ai_memory_window).lower() != "unlimited":
                try:
                    import re
                    match = re.search(r'\d+', str(setting.ai_memory_window))
                    if match:
                        memory_window_days = int(match.group())
                except Exception:
                    pass
                    
        # Filter messages by memory window
        if memory_window_days:
            from datetime import timedelta, timezone
            now = datetime.now(timezone.utc)
            cutoff_date = now - timedelta(days=memory_window_days)
            filtered = []
            for m in messages:
                created_at = m.get("created_at")
                if created_at:
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=timezone.utc)
                    if created_at < cutoff_date:
                        continue
                filtered.append(m)
            messages = filtered

        owner_id_str = str(user_id)
        summary = await self.summarize(messages, owner_id=owner_id_str, system_rules=system_rules)
        entities = await self.extract_entities(messages, owner_id=owner_id_str, system_rules=system_rules)
        relationship_score = self.calculate_relationship_score(messages)
        timeline = self.build_timeline(messages)

        # Lấy giới hạn số lượng tag từ cấu hình của user
        tag_limit = 6
        if db:
            ai_config = db.query(AISystemConfig).filter(
                AISystemConfig.user_id == user_id,
                AISystemConfig.key == "ai_settings"
            ).first()
            if ai_config and isinstance(ai_config.value, dict):
                tag_limit = int(ai_config.value.get("tag_limit", 6))

        interested_in = entities.get("interested_in", [])[:tag_limit]

        # Build facts dictionary
        facts = {
            "last_met": entities.get("last_met"),
            "interested_in": interested_in,
            "follow_up": entities.get("follow_up"),
            "timeline": timeline,
            "relationship_score": relationship_score,
        }

        result = MemoryResult(
            summary=summary,
            last_met=entities.get("last_met"),
            interested_in=interested_in,
            follow_up=entities.get("follow_up"),
            timeline=timeline,
            relationship_score=relationship_score,
        )
        # Monkey patch facts onto result for worker compatibility
        result.facts = facts

        logger.info(
            "Memory built for user_id=%s: score=%d, interests=%d",
            user_id,
            result.relationship_score,
            len(result.interested_in),
        )

        return result
