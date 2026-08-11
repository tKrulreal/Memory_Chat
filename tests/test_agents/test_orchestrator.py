"""
Tests cho Assistant Orchestrator (WS-05 TASK-COP-01).
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.orchestrator import (
    Intent,
    _classify_intent,
    _generate_chitchat_response,
    agent_execution_node,
    build_orchestrator,
    context_builder_node,
    intent_detection_node,
    respond_node,
    response_validator_node,
    run_copilot,
    tool_selection_node,
)
from src.agents.state import AgentState


class TestIntentClassification:
    """Test intent classification logic."""

    def test_classify_search_intent(self):
        """Từ khóa tìm kiếm → SEARCH intent."""
        llm = MagicMock()
        intent, conf = _classify_intent("tìm người làm AI ở Hà Nội", llm)
        assert intent == Intent.SEARCH
        assert conf >= 0.8

    def test_classify_memory_intent(self):
        """Từ khóa về memory → MEMORY intent."""
        llm = MagicMock()
        intent, conf = _classify_intent("người này là ai", llm)
        assert intent == Intent.MEMORY
        assert conf >= 0.8

    def test_classify_reply_suggest_intent(self):
        """Từ khóa về reply → REPLY_SUGGEST intent."""
        llm = MagicMock()
        intent, conf = _classify_intent("tôi nên nhắn gì", llm)
        assert intent == Intent.REPLY_SUGGEST
        assert conf >= 0.8

    def test_classify_chitchat_intent(self):
        """Từ khóa chào hỏi → CHITCHAT intent."""
        llm = MagicMock()
        intent, conf = _classify_intent("chào bạn", llm)
        assert intent == Intent.CHITCHAT
        assert conf >= 0.8

    def test_classify_recommendation_intent(self):
        """Từ khóa gợi ý → RECOMMENDATION intent."""
        llm = MagicMock()
        intent, conf = _classify_intent("ai cần follow-up", llm)
        assert intent == Intent.RECOMMENDATION
        assert conf >= 0.8

    def test_classify_tag_intent(self):
        """Từ khóa tag → TAG_SUGGEST intent."""
        llm = MagicMock()
        intent, conf = _classify_intent("gợi ý tag cho người này", llm)
        assert intent == Intent.TAG_SUGGEST
        assert conf >= 0.8


class TestChitchatResponses:
    """Test chitchat response generation."""

    def test_chitchat_greeting(self):
        resp = _generate_chitchat_response("chào bạn")
        assert "Chào" in resp or "Hi" in resp

    def test_chitchat_thanks(self):
        resp = _generate_chitchat_response("cảm ơn bạn")
        assert "không có gì" in resp.lower() or "welcome" in resp.lower()

    def test_chitchat_bye(self):
        resp = _generate_chitchat_response("tạm biệt")
        # Mình hiểu rồi fallback → acceptable
        assert len(resp) > 5


class TestOrchestratorNodes:
    """Test LangGraph nodes."""

    def _run(self, coro):
        return asyncio.run(coro)

    @pytest.mark.asyncio
    async def test_intent_detection_empty_query(self):
        state = AgentState(query="", context={})
        result = await intent_detection_node(state)
        assert result["intent"] == Intent.UNKNOWN.value
        assert result["intent_confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_intent_detection_search_query(self):
        state = AgentState(query="tìm người làm AI", context={})
        result = await intent_detection_node(state)
        assert result["intent"] == Intent.SEARCH.value
        assert "confidence" in result["intent_reasoning"]

    @pytest.mark.asyncio
    async def test_intent_detection_chitchat(self):
        state = AgentState(query="chào bạn", context={})
        result = await intent_detection_node(state)
        assert result["intent"] == Intent.CHITCHAT.value

    @pytest.mark.asyncio
    async def test_context_builder_no_context(self):
        """No context provided → returns default message."""
        state = AgentState(query="test", context={})
        result = await context_builder_node(state)
        assert "context_data" in result
        assert "Không có context" in result["context_data"]

    @pytest.mark.asyncio
    async def test_tool_selection_search_intent(self):
        state = AgentState(query="tìm người", intent=Intent.SEARCH.value, context={})
        result = await tool_selection_node(state)
        assert "search_contact" in result["tools_to_call"]

    @pytest.mark.asyncio
    async def test_tool_selection_memory_intent(self):
        state = AgentState(
            query="người này là ai",
            intent=Intent.MEMORY.value,
            context={"contact_id": "test-uuid"},
        )
        result = await tool_selection_node(state)
        assert "get_contact_memory" in result["tools_to_call"]

    @pytest.mark.asyncio
    async def test_tool_selection_recommendation_intent(self):
        state = AgentState(query="ai cần follow-up", intent=Intent.RECOMMENDATION.value, context={})
        result = await tool_selection_node(state)
        assert "get_recommendations" in result["tools_to_call"]

    @pytest.mark.asyncio
    async def test_tool_selection_chitchat(self):
        state = AgentState(query="chào", intent=Intent.CHITCHAT.value, context={})
        result = await tool_selection_node(state)
        assert result["tools_to_call"] == []

    @pytest.mark.asyncio
    async def test_agent_execution_no_tools(self):
        state = AgentState(query="test", tools_to_call=[], context={})
        result = await agent_execution_node(state)
        assert result["execution_summary"] == "No tools to execute"
        assert result["agent_responses"] == {}

    @pytest.mark.asyncio
    async def test_response_validator_valid(self):
        state = AgentState(
            query="test",
            execution_summary="Some valid response",
        )
        result = await response_validator_node(state)
        assert result["is_valid"] is True

    @pytest.mark.asyncio
    async def test_response_validator_chitchat(self):
        """Chitchat skips validation."""
        state = AgentState(
            query="chào bạn",
            intent=Intent.CHITCHAT.value,
            execution_summary="",
        )
        result = await response_validator_node(state)
        assert result["is_valid"] is True

    @pytest.mark.asyncio
    async def test_respond_chitchat(self):
        state = AgentState(
            query="chào bạn",
            intent=Intent.CHITCHAT.value,
            context={},
        )
        result = await respond_node(state)
        assert "response" in result
        assert "final_response" in result
        # Should be a greeting
        assert len(result["final_response"]) > 5

    @pytest.mark.asyncio
    async def test_respond_no_tools(self):
        """No tools executed → returns fallback message."""
        state = AgentState(
            query="test",
            intent=Intent.UNKNOWN.value,
            execution_summary="No tools to execute",
            context={},
        )
        result = await respond_node(state)
        assert "response" in result
        # Should indicate no info
        assert "không" in result["response"].lower() or "info" in result["response"].lower()


class TestOrchestratorGraph:
    """Test the full orchestrator graph."""

    def test_build_orchestrator_returns_compiled_graph(self):
        graph = build_orchestrator()
        assert graph is not None
        assert callable(graph.ainvoke)

    def _run(self, coro):
        return asyncio.run(coro)

    @pytest.mark.asyncio
    async def test_run_copilot_with_context(self):
        """Test run_copilot convenience function."""
        with patch("src.agents.orchestrator.orchestrator") as mock_graph:
            mock_graph.ainvoke = AsyncMock(return_value={
                "final_response": "Test response",
                "intent": Intent.CHITCHAT.value,
                "tools_to_call": [],
                "is_valid": True,
            })

            result = await run_copilot(
                query="chào bạn",
                user_id="test-user",
            )

            assert result["response"] == "Test response"
            assert result["intent"] == Intent.CHITCHAT.value
            assert result["is_valid"] is True

    @pytest.mark.asyncio
    async def test_run_copilot_minimal(self):
        """Test run_copilot with minimal params."""
        with patch("src.agents.orchestrator.orchestrator") as mock_graph:
            mock_graph.ainvoke = AsyncMock(return_value={
                "final_response": "Minimal response",
                "intent": Intent.UNKNOWN.value,
                "tools_to_call": [],
                "is_valid": True,
            })

            result = await run_copilot(query="test")
            assert "response" in result
