"""
Tests cho AI Tools (WS-05 TASK-COP-02).
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest


class TestSearchTools:
    """Test search tools."""

    def test_search_contact_tool_exists(self):
        """search_contact tool exists and has correct interface."""
        from src.agents.tools.search_tools import search_contact

        # LangChain @tool returns StructuredTool
        assert hasattr(search_contact, "name")
        assert hasattr(search_contact, "invoke")
        assert search_contact.name == "search_contact"


class TestMemoryTools:
    """Test memory tools."""

    def test_get_contact_memory_invalid_user_uuid(self):
        """Invalid user UUID → error message."""
        from src.agents.tools.memory_tools import get_contact_memory

        result = get_contact_memory.invoke({
            "user_id": "not-a-uuid",
            "contact_id": str(uuid.uuid4()),
        })
        assert "Invalid" in result

    def test_get_contact_memory_invalid_contact_uuid(self):
        """Invalid contact UUID → error message."""
        from src.agents.tools.memory_tools import get_contact_memory

        result = get_contact_memory.invoke({
            "user_id": str(uuid.uuid4()),
            "contact_id": "not-a-uuid",
        })
        assert "Invalid" in result

    def test_get_contact_memory_no_memory(self):
        """Contact has no memory → message."""
        from src.agents.tools.memory_tools import get_contact_memory

        mock_contact = MagicMock()
        mock_contact.user_id = uuid.uuid4()

        mock_db = MagicMock()
        mock_db.get.return_value = mock_contact
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch("src.agents.tools.memory_tools._get_db", return_value=mock_db):
            result = get_contact_memory.invoke({
                "user_id": str(mock_contact.user_id),
                "contact_id": str(uuid.uuid4()),
            })
            assert "Chưa có memory" in result

    def test_get_recent_messages_invalid_user_uuid(self):
        """Invalid user UUID → error message."""
        from src.agents.tools.memory_tools import get_recent_messages

        result = get_recent_messages.invoke({
            "user_id": "invalid",
            "conversation_id": str(uuid.uuid4()),
        })
        assert "Invalid" in result


class TestRecommendationTools:
    """Test recommendation tools."""

    def test_get_recommendations_empty(self):
        """No recommendations → informative message."""
        from src.agents.tools.recommendation_tools import get_recommendations

        with patch("src.agents.tools.recommendation_tools._get_db") as mock_get_db:
            mock_db = MagicMock()
            mock_db.execute.return_value.all.return_value = []
            mock_get_db.return_value = mock_db

            result = get_recommendations.invoke({
                "user_id": str(uuid.uuid4()),
                "status": "PENDING",
                "limit": 10,
            })
            assert "Không có recommendation" in result


class TestInsightTools:
    """Test insight tools."""

    def test_get_contact_insights_invalid_uuid(self):
        """Invalid UUID → error message."""
        from src.agents.tools.insight_tools import get_contact_insights

        result = get_contact_insights.invoke({"contact_id": "invalid"})
        assert "Invalid" in result


class TestToolRegistry:
    """Test tool registry."""

    def test_tool_registry_has_tools(self):
        """TOOL_REGISTRY contains expected tools."""
        from src.agents.tools import TOOL_REGISTRY

        tool_names = [t.name for t in TOOL_REGISTRY]

        assert "search_contact" in tool_names
        assert "semantic_search" in tool_names
        assert "get_contact_memory" in tool_names
        assert "get_recent_messages" in tool_names
        assert "get_recommendations" in tool_names
        assert "recommend_reply" in tool_names
        assert "get_contact_insights" in tool_names

    def test_all_tools_are_callable(self):
        """All tools in registry have expected LangChain interface."""
        from src.agents.tools import TOOL_REGISTRY

        for tool in TOOL_REGISTRY:
            # LangChain @tool returns StructuredTool, not raw callable
            assert hasattr(tool, "name"), f"Tool has no name attribute"
            assert hasattr(tool, "invoke"), f"Tool {tool.name} has no invoke method"
            # invoke should be callable
            assert callable(tool.invoke), f"Tool.invoke is not callable for {tool.name}"
