"""
AI Copilot Agent (Simplified for Phase 4)
Thay thế hoàn toàn LangGraph phức tạp bằng luồng xử lý Agent đơn giản, an toàn.
"""

import json
import logging
import uuid
from enum import StrEnum

from src.gateways.llm import LLMGateway
from src.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class Intent(StrEnum):
    SEARCH = "SEARCH"
    MEMORY = "MEMORY"
    CHITCHAT = "CHITCHAT"
    UNKNOWN = "UNKNOWN"


SYSTEM_PROMPT = """Bạn là AI Copilot trong ứng dụng nhắn tin MemoryChat.
Nhiệm vụ: Trả lời câu hỏi của người dùng dựa trên lịch sử trò chuyện đã được cung cấp.
Không bịa đặt thông tin. Nếu không có thông tin, hãy nói rõ.
Trả lời ngắn gọn, thân thiện, và trực tiếp vào câu hỏi.
"""


def _classify_intent(query: str, llm: LLMGateway) -> Intent:
    query_lower = query.lower().strip()
    
    keyword_rules = [
        (["tìm", "tìm kiếm", "search"], Intent.SEARCH),
        (["chào", "cảm ơn", "hello", "hi", "bye"], Intent.CHITCHAT),
    ]

    for keywords, intent in keyword_rules:
        if any(kw in query_lower for kw in keywords):
            return intent

    return Intent.MEMORY


def _get_context_from_memory(query: str, user_id: str, conversation_id: str | None) -> str:
    """Lấy context từ vector database dựa trên query."""
    if not conversation_id:
        return "Không có thông tin lịch sử phù hợp (thiếu conversation_id)."

    llm = LLMGateway()
    vector_store = VectorStoreService.get_instance()
    
    try:
        query_embedding = llm.embed(query)
            
        results = vector_store.query(
            query_embedding=query_embedding,
            owner_user_id=user_id,
            conversation_id=conversation_id,
            top_k=3
        )
        
        if not results.documents:
            return "Không có thông tin lịch sử phù hợp."
            
        return "\n\n".join(results.documents)
    except Exception as e:
        logger.error(f"Failed to fetch memory context: {e}")
        return "Không thể truy xuất bộ nhớ."


async def run_copilot(
    query: str,
    user_id: str | None = None,
    contact_id: str | None = None,
    conversation_id: str | None = None,
) -> dict:
    """
    Simple Copilot logic:
    1. Detect intent
    2. If Chitchat -> basic reply
    3. If Memory/Search -> Embed query, search ChromaDB with owner_user_id, then LLM reply.
    """
    if not user_id:
        return {
            "response": "Thiếu user_id để thực hiện Copilot.",
            "intent": "ERROR",
            "is_valid": False,
        }

    llm = LLMGateway()
    intent = _classify_intent(query, llm)

    if intent == Intent.CHITCHAT:
        return {
            "response": "Xin chào! 👋 Mình là trợ lý AI. Mình có thể giúp gì cho bạn?",
            "intent": intent.value,
            "is_valid": True,
        }

    # Memory/Search Intent
    memory_context = _get_context_from_memory(query, user_id, conversation_id)
    
    prompt = f"""{SYSTEM_PROMPT}

[NGỮ CẢNH LỊCH SỬ]
{memory_context}

[CÂU HỎI CỦA NGƯỜI DÙNG]
{query}
"""

    try:
        response = llm.chat(prompt, "")
        return {
            "response": response,
            "intent": intent.value,
            "tools_used": ["vector_search"],
            "is_valid": True,
        }
    except Exception as e:
        logger.error(f"LLM chat failed: {e}")
        return {
            "response": "Xin lỗi, hệ thống đang bận. Vui lòng thử lại sau.",
            "intent": "ERROR",
            "is_valid": False,
        }
