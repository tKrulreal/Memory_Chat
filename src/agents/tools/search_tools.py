"""
Search tools cho AI Agents.

Dùng LangChain @tool decorator.
"""

import logging
from typing import Annotated

from langchain_core.tools import tool

from src.agents.search.agent import SearchAgent

logger = logging.getLogger(__name__)

# Singleton SearchAgent instance
_search_agent: SearchAgent | None = None


def _get_search_agent() -> SearchAgent:
    global _search_agent
    if _search_agent is None:
        _search_agent = SearchAgent()
    return _search_agent


@tool
def search_contact(
    query: Annotated[str, "Câu hỏi hoặc mô tả về contact cần tìm. Ví dụ: 'người làm AI ở Hà Nội'"],
    limit: Annotated[int, "Số lượng kết quả tối đa"] = 5,
) -> str:
    """
    Tìm kiếm contacts dựa trên mô tả ngữ nghĩa.

    Dùng khi người dùng muốn tìm một contact cụ thể
    mà không nhớ tên chính xác, ví dụ:
    - "người làm AI ở Hà Nội"
    - "bạn từng trao đổi về startup"
    - "người quan tâm đến blockchain"

    Args:
        query: Câu mô tả ngữ nghĩa về contact cần tìm
        limit: Số lượng kết quả trả về (mặc định 5)

    Returns:
        Danh sách contacts phù hợp dạng text
    """
    agent = _get_search_agent()

    try:
        import asyncio
        results = asyncio.get_event_loop().run_until_complete(
            agent.search(query, limit=limit)
        )

        if not results:
            return "Không tìm thấy contact nào phù hợp với mô tả."

        output_lines = [f"Tìm thấy {len(results)} contact phù hợp:"]
        for i, r in enumerate(results, 1):
            output_lines.append(
                f"{i}. {r.name} (contact_id: {r.contact_id}) - "
                f"Độ phù hợp: {r.score}%\n   Giải thích: {r.explanation}"
            )
        return "\n".join(output_lines)

    except Exception as e:
        logger.error(f"search_contact failed: {e}")
        return f"Lỗi khi tìm kiếm: {str(e)}"


@tool
def semantic_search(
    query: Annotated[str, "Câu hỏi hoặc từ khóa tìm kiếm"],
    limit: Annotated[int, "Số kết quả tối đa"] = 5,
) -> str:
    """
    Semantic search toàn bộ memories và conversations.

    Dùng khi người dùng muốn tìm thông tin cụ thể
    đã được nhớ từ cuộc trò chuyện trước đó.

    Args:
        query: Câu hỏi hoặc từ khóa
        limit: Số kết quả tối đa

    Returns:
        Kết quả tìm kiếm dạng text
    """
    return search_contact.invoke({"query": query, "limit": limit})
