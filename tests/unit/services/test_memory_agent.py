"""
Tests cho MemoryAgent.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.memory import MemoryAgent, MemoryResult
from src.agents.memory.agent import (
    chunk_messages,
    estimate_tokens,
    format_conversation_for_prompt,
)


class TestMemoryAgentHelpers:
    def test_estimate_tokens(self):
        assert estimate_tokens("Hello world") == 2  # ~8 chars / 4 = 2
        assert estimate_tokens("a" * 400) == 100  # 400 chars / 4 = 100

    def test_chunk_messages(self):
        messages = [
            {"content": "Hello", "sender_type": "USER", "created_at": datetime.now(timezone.utc)},
            {"content": "Hi", "sender_type": "CONTACT", "created_at": datetime.now(timezone.utc)},
            {"content": "How are you?", "sender_type": "USER", "created_at": datetime.now(timezone.utc)},
            {"content": "I'm fine thanks!", "sender_type": "CONTACT", "created_at": datetime.now(timezone.utc)},
            {"content": "What do you do?", "sender_type": "USER", "created_at": datetime.now(timezone.utc)},
        ]
        chunks = chunk_messages(messages, max_tokens=500)
        # All 5 messages should fit in 1 chunk (~50 chars total)
        assert len(chunks) == 1
        assert len(chunks[0]) == 5

    def test_chunk_messages_long(self):
        # Create messages that exceed max_tokens
        messages = [
            {"content": "x" * 2000, "sender_type": "USER", "created_at": datetime.now(timezone.utc)}
            for _ in range(3)
        ]
        chunks = chunk_messages(messages, max_tokens=500)
        # Each message ~500 tokens, should be split
        assert len(chunks) >= 2

    def test_format_conversation(self):
        messages = [
            {"content": "Hello", "sender_type": "USER", "created_at": None},
            {"content": "Hi there", "sender_type": "CONTACT", "created_at": datetime(2026, 8, 3, 10, 0, 0, tzinfo=timezone.utc)},
        ]
        text = format_conversation_for_prompt(messages)
        assert "[USER]" in text
        assert "[CONTACT]" in text
        assert "Hello" in text
        assert "03/08/2026" in text


class TestMemoryAgent:
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM Gateway."""
        llm = MagicMock()
        llm.complete = AsyncMock(return_value="Mocked summary")
        return llm

    @pytest.fixture
    def agent(self, mock_llm):
        return MemoryAgent(llm=mock_llm)

    def test_calculate_relationship_score_empty(self, agent):
        score = agent.calculate_relationship_score([])
        assert score == 0

    def test_calculate_relationship_score_low(self, agent):
        messages = [
            {"content": "Hi", "sender_type": "USER", "created_at": datetime.now(timezone.utc)},
            {"content": "Hello", "sender_type": "CONTACT", "created_at": datetime.now(timezone.utc)},
        ]
        score = agent.calculate_relationship_score(messages)
        assert 0 <= score <= 100
        assert score > 0

    def test_calculate_relationship_score_high(self, agent):
        # Many messages with positive words
        messages = [
            {
                "content": f"Message {i} - cảm ơn bạn rất nhiều!",
                "sender_type": "USER" if i % 2 == 0 else "CONTACT",
                "created_at": datetime.now(timezone.utc),
            }
            for i in range(20)
        ]
        score = agent.calculate_relationship_score(messages)
        assert score > 30  # Should have accumulated points

    def test_build_timeline_empty(self, agent):
        result = agent.build_timeline([])
        assert result == []

    def test_build_timeline(self, agent):
        messages = [
            {
                "content": "Hello",
                "sender_type": "USER",
                "created_at": datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc),
            },
            {
                "content": "Hi",
                "sender_type": "CONTACT",
                "created_at": datetime(2026, 8, 1, 10, 5, 0, tzinfo=timezone.utc),
            },
            {
                "content": "How are you?",
                "sender_type": "USER",
                "created_at": datetime(2026, 8, 2, 11, 0, 0, tzinfo=timezone.utc),
            },
        ]
        timeline = agent.build_timeline(messages)
        assert len(timeline) == 2  # 2 distinct dates
        assert timeline[0]["date"] == "2026-08-01"
        assert timeline[0]["message_count"] == 2
        assert timeline[1]["date"] == "2026-08-02"
        assert timeline[1]["message_count"] == 1

    def test_parse_json_response_valid(self, agent):
        raw = '{"company": "VinUni", "profession": "Student", "skills": ["Python"], "interests": ["AI"]}'
        result = agent._parse_json_response(raw)
        assert result["company"] == "VinUni"
        assert result["skills"] == ["Python"]

    def test_parse_json_response_markdown(self, agent):
        raw = '```json\n{"company": "VinUni", "skills": ["Python"]}\n```'
        result = agent._parse_json_response(raw)
        assert result["company"] == "VinUni"

    def test_parse_json_response_invalid(self, agent):
        raw = "This is not JSON at all"
        result = agent._parse_json_response(raw)
        assert result is None

    def test_merge_entity_results_empty(self, agent):
        result = agent._merge_entity_results([])
        assert result == {"company": None, "profession": None, "skills": [], "interests": []}

    def test_merge_entity_results_single(self, agent):
        result = agent._merge_entity_results([
            {"company": "VinUni", "profession": "Student", "skills": ["Python"], "interests": ["AI"]}
        ])
        assert result["company"] == "VinUni"
        assert result["skills"] == ["Python"]

    def test_merge_entity_results_multiple(self, agent):
        result = agent._merge_entity_results([
            {"company": "VinUni", "skills": ["Python", "React"]},
            {"company": "VinUni", "skills": ["Python", "Go"]},
        ])
        assert result["company"] == "VinUni"
        # Should deduplicate Python
        skills_lower = [s.lower() for s in result["skills"]]
        assert "python" in skills_lower
        assert len(result["skills"]) == 3  # Python, React, Go

    @pytest.mark.asyncio
    async def test_summarize_empty(self, agent):
        result = await agent.summarize([])
        assert result == "Không có hội thoại để tóm tắt."

    @pytest.mark.asyncio
    async def test_build_memory(self, agent):
        contact_id = uuid.uuid4()
        messages = [
            {
                "content": "Tôi là sinh viên năm 3 tại VinUni",
                "sender_type": "USER",
                "created_at": datetime.now(timezone.utc),
            },
            {
                "content": "Bạn học ngành gì?",
                "sender_type": "CONTACT",
                "created_at": datetime.now(timezone.utc),
            },
        ]

        with patch.object(agent, "extract_entities", new_callable=AsyncMock) as mock_extract:
            mock_extract.return_value = {
                "company": "VinUni",
                "profession": "Student",
                "skills": ["Python"],
                "interests": ["AI"],
            }
            result = await agent.build_memory(contact_id, messages)

        assert isinstance(result, MemoryResult)
        assert result.company == "VinUni"
        assert result.profession == "Student"
        assert "Python" in result.skills
        assert result.relationship_score >= 0
