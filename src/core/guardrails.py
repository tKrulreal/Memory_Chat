"""
Guardrails System for MemoryChat AI Copilot.

Provides:
1. Input Guardrails: Anti-jailbreak, query length limits, and conversation access control.
2. In-Chat Isolation Guardrails: Strict boundary enforcement per conversation.
3. Global Copilot Guardrails: Public profile & user-scoped memory privacy enforcement.
4. Output Guardrails: Sensitive data/credential redaction and empty response fallbacks.
"""

import logging
import re
import uuid
from typing import Any
from sqlalchemy.orm import Session

from src.models.chat import Conversation

logger = logging.getLogger(__name__)

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|prompts|rules)",
    r"disregard\s+(all\s+)?(previous|prior)\s+(instructions|prompts|rules)",
    r"you\s+are\s+now\s+(a\s+)?(hacker|dan|developer\s+mode|unrestricted)",
    r"reveal\s+(your\s+)?(system\s+prompt|instructions|api\s+key|secret)",
    r"show\s+me\s+the\s+system\s+prompt",
    r"act\s+as\s+root",
    r"override\s+system\s+prompt",
    r"system:\s*ignore",
    r"print\s+environment\s+variables",
    r"dump\s+(all\s+)?(database|passwords|tokens)",
]

SENSITIVE_CREDENTIAL_PATTERNS = [
    (r"(?i)(bearer\s+[a-zA-Z0-9_\-\.]{20,})", "[REDACTED_TOKEN]"),
    (r"(?i)(password\s*[:=]\s*['\"][^'\"]+['\"])", "password: [REDACTED]"),
    (r"(?i)(api[_-]?key\s*[:=]\s*['\"][^'\"]+['\"])", "api_key: [REDACTED]"),
    (r"(?i)(secret[_-]?key\s*[:=]\s*['\"][^'\"]+['\"])", "secret_key: [REDACTED]"),
    (r"(?i)(postgres(ql)?://[^\s'\"]+)", "[REDACTED_DATABASE_URL]"),
    (r"(\$2[aby]\$[0-9]{2}\$[a-zA-Z0-9\./]{53})", "[REDACTED_PASSWORD_HASH]"),
]


class GuardrailException(Exception):
    def __init__(self, message: str, code: str = "GUARDRAIL_VIOLATION"):
        super().__init__(message)
        self.message = message
        self.code = code


def validate_input_query(query: str, max_length: int = 2000) -> str:
    if not query or not query.strip():
        raise GuardrailException("Câu hỏi không được để trống.", code="EMPTY_QUERY")

    sanitized = query.strip()
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, sanitized, re.IGNORECASE):
            logger.warning(f"Prompt injection pattern detected: '{pattern}' in query: '{sanitized[:80]}'")
            raise GuardrailException(
                "Yêu cầu của bạn chứa các câu lệnh không được hỗ trợ để đảm bảo an toàn hệ thống.",
                code="PROMPT_INJECTION_DETECTED"
            )

    return sanitized


def verify_in_chat_access(
    db: Session,
    user_id: uuid.UUID | str,
    conversation_id: uuid.UUID | str | None,
) -> Conversation:
    if not conversation_id:
        raise GuardrailException("Thiếu conversation_id cho In-Chat Copilot.", code="MISSING_CONVERSATION_ID")

    try:
        conv_uuid = uuid.UUID(str(conversation_id))
    except ValueError:
        raise GuardrailException("conversation_id không hợp lệ.", code="INVALID_CONVERSATION_ID")

    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError:
        raise GuardrailException("user_id không hợp lệ.", code="INVALID_USER_ID")

    conv = db.get(Conversation, conv_uuid)
    if not conv:
        raise GuardrailException("Cuộc trò chuyện không tồn tại.", code="CONVERSATION_NOT_FOUND")

    if conv.user_a_id != user_uuid and conv.user_b_id != user_uuid:
        logger.warning(f"Unauthorized In-Chat Copilot access attempt: User {user_uuid} on Conv {conv_uuid}")
        raise GuardrailException("Bạn không có quyền truy cập vào cuộc trò chuyện này.", code="UNAUTHORIZED_ACCESS")

    return conv


def sanitize_output_response(
    response_text: str,
    default_fallback: str = "Đã hoàn thành phân tích nhưng không tìm thấy dữ liệu phù hợp."
) -> str:
    if not response_text or not response_text.strip():
        return default_fallback

    cleaned = response_text.strip()
    for pattern, replacement in SENSITIVE_CREDENTIAL_PATTERNS:
        cleaned = re.sub(pattern, replacement, cleaned)

    return cleaned
