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
from src.models.contact import ContactMemory

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


def format_conversation_for_prompt(messages: list[dict[str, Any]]) -> str:
    """Format messages thành text để đưa vào prompt."""
    lines = []
    for msg in messages:
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
    company: str | None = None
    profession: str | None = None
    skills: list[str] = field(default_factory=list)
    interests: list[str] = field(default_factory=list)
    timeline: list[dict[str, Any]] = field(default_factory=list)
    relationship_score: int = 50  # 0-100

    def to_contact_memory_dict(self, contact_id: uuid.UUID) -> dict[str, Any]:
        """Convert sang dict để lưu vào ContactMemory."""
        return {
            "contact_id": contact_id,
            "summary": self.summary,
            "profession": self.profession,
            "company": self.company,
            "skills": {"skills": self.skills},
            "interest": {"interests": self.interests},
            "timeline": {"events": self.timeline},
            "relationship_score": self.relationship_score,
        }


# --- Prompt templates ---
MEMORY_SUMMARY_PROMPT = """Bạn là một AI assistant chuyên phân tích hội thoại để tạo contact memory.

Hội thoại:
{conversation}

Hãy đọc hội thoại trên và tạo một bản tóm tắt ngắn gọn (2-3 câu) về người này.
Bản tóm tắt nên bao gồm:
- Họ là ai (nếu biết)
- Tính cách / phong cách giao tiếp
- Chủ đề họ quan tâm

Trả lời CHỈ bằng tiếng Việt, không giải thích thêm.
"""

MEMORY_ENTITIES_PROMPT = """Bạn là một AI assistant chuyên trích xuất thông tin cá nhân từ hội thoại.

Hội thoại:
{conversation}

Hãy trích xuất các thông tin sau (chỉ trả về JSON):
{{
    "company": "Tên công ty/ tổ chức (nếu có, nếu không thì null)",
    "profession": "Nghề nghiệp/ vai trò (nếu có, nếu không thì null)",
    "skills": ["danh sách kỹ năng, sở thích (nếu có, mảng rỗng nếu không có)"],
    "interests": ["danh sách chủ đề người này quan tâm (nếu có, mảng rỗng nếu không có)"]
}}

Trả lời CHỈ bằng JSON, không giải thích thêm.
"""


class MemoryAgent:
    """
    Memory Agent — phân tích conversation và sinh ContactMemory.

    Usage:
        agent = MemoryAgent()
        result = await agent.build_memory(contact_id, messages)
    """

    def __init__(self, llm: LLMGateway | None = None):
        self._llm = llm or LLMGateway()

    async def summarize(self, messages: list[dict[str, Any]]) -> str:
        """
        Tóm tắt conversation.

        Args:
            messages: List of {content, sender_type, created_at}

        Returns:
            Summary string
        """
        if not messages:
            return "Không có hội thoại để tóm tắt."

        # Chunk nếu quá dài
        chunks = chunk_messages(messages, max_tokens=500)
        summaries = []

        for i, chunk in enumerate(chunks):
            text = format_conversation_for_prompt(chunk)
            prompt = MEMORY_SUMMARY_PROMPT.format(conversation=text)
            try:
                summary = self._llm.complete(prompt)
                summaries.append(summary.strip())
            except Exception as e:
                logger.warning("LLM summarize failed for chunk %d: %s", i, e)
                summaries.append("")

        if len(summaries) == 1:
            return summaries[0]

        # Nếu có nhiều chunks, tóm tắt lại
        combined = " ".join(s for s in summaries if s)
        if not combined:
            return "Không thể tạo tóm tắt."

        final_prompt = (
            f"Bạn hãy tóm tắt ngắn gọn các ý sau thành 1 đoạn (2-3 câu):\n{combined}"
        )
        try:
            return self._llm.complete(final_prompt).strip()
        except Exception as e:
            logger.warning("LLM final summarize failed: %s", e)
            return combined[:200]

    async def extract_entities(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Trích xuất entities từ conversation.

        Args:
            messages: List of {content, sender_type, created_at}

        Returns:
            Dict với keys: company, profession, skills, interests
        """
        if not messages:
            return {"company": None, "profession": None, "skills": [], "interests": []}

        chunks = chunk_messages(messages, max_tokens=500)
        all_results: list[dict[str, Any]] = []

        for i, chunk in enumerate(chunks):
            text = format_conversation_for_prompt(chunk)
            prompt = MEMORY_ENTITIES_PROMPT.format(conversation=text)
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
            return {"company": None, "profession": None, "skills": [], "interests": []}
        if len(results) == 1:
            r = results[0]
            return {
                "company": r.get("company"),
                "profession": r.get("profession"),
                "skills": r.get("skills", []),
                "interests": r.get("interests", []),
            }

        # Collect from all
        companies = [r["company"] for r in results if r.get("company")]
        professions = [r["profession"] for r in results if r.get("profession")]
        all_skills: list[str] = []
        all_interests: list[str] = []
        seen_skills: set[str] = set()
        seen_interests: set[str] = set()

        for r in results:
            skills = r.get("skills") or []
            for skill in skills:
                norm = str(skill).strip().lower()
                if norm and norm not in seen_skills:
                    seen_skills.add(norm)
                    all_skills.append(str(skill).strip())
            interests = r.get("interests") or []
            for interest in interests:
                norm = str(interest).strip().lower()
                if norm and norm not in seen_interests:
                    seen_interests.add(norm)
                    all_interests.append(str(interest).strip())

        return {
            "company": companies[0] if companies else None,
            "profession": professions[0] if professions else None,
            "skills": all_skills[:20],  # Limit
            "interests": all_interests[:20],
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
        contact_id: uuid.UUID,
        messages: list[dict[str, Any]],
    ) -> MemoryResult:
        """
        Tổng hợp — gọi tất cả methods và trả về MemoryResult.

        Args:
            contact_id: UUID của contact
            messages: List of {content, sender_type, created_at}

        Returns:
            MemoryResult với tất cả fields
        """
        logger.info("Building memory for contact_id=%s with %d messages", contact_id, len(messages))

        summary = await self.summarize(messages)
        entities = await self.extract_entities(messages)
        relationship_score = self.calculate_relationship_score(messages)
        timeline = self.build_timeline(messages)

        result = MemoryResult(
            summary=summary,
            company=entities.get("company"),
            profession=entities.get("profession"),
            skills=entities.get("skills", []),
            interests=entities.get("interests", []),
            timeline=timeline,
            relationship_score=relationship_score,
        )

        logger.info(
            "Memory built for contact_id=%s: score=%d, skills=%d, interests=%d",
            contact_id,
            result.relationship_score,
            len(result.skills),
            len(result.interests),
        )

        return result
