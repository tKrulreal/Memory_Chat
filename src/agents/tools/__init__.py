"""
Tools package cho AI Agents.

Mỗi tool wrap một Agent hoặc repository operation,
dùng LangChain @tool decorator.

Tool registry để Orchestrator có thể bind vào graph.
"""

from src.agents.tools.search_tools import (
    search_contact,
    semantic_search,
)
from src.agents.tools.memory_tools import (
    get_contact_memory,
    get_recent_messages,
)
from src.agents.tools.recommendation_tools import (
    get_recommendations,
    recommend_reply,
)
from src.agents.tools.insight_tools import get_contact_insights

# Tool registry — tất cả tools để bind vào LangGraph
TOOL_REGISTRY = [
    search_contact,
    semantic_search,
    get_contact_memory,
    get_recent_messages,
    get_recommendations,
    recommend_reply,
    get_contact_insights,
]

__all__ = [
    "search_contact",
    "semantic_search",
    "get_contact_memory",
    "get_recent_messages",
    "get_recommendations",
    "recommend_reply",
    "get_contact_insights",
    "TOOL_REGISTRY",
]
