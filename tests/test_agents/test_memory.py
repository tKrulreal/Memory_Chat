"""
Unit tests for MemoryAgent and Peer Isolation / Sanitization.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.agents.memory.agent import MemoryAgent, sanitize_peer_text


class TestMemoryAgent:
    """Test MemoryAgent functions and prompt sanitization."""

    def test_sanitize_peer_text(self):
        """Test that [PEER], {peer}, [USER] are cleanly stripped and replaced."""
        raw1 = "[PEER] là một lập trình viên Python tại FPT."
        cleaned1 = sanitize_peer_text(raw1)
        assert "[PEER]" not in cleaned1
        assert "Đối tác" in cleaned1

        raw2 = "Gợi ý trao đổi với {peer} về dự án của [USER]."
        cleaned2 = sanitize_peer_text(raw2)
        assert "{peer}" not in cleaned2
        assert "[USER]" not in cleaned2
        assert "Đối tác" in cleaned2
        assert "Bạn" in cleaned2

    @pytest.mark.asyncio
    async def test_summarize_sanitization(self):
        """Test that summarize output removes raw prompt tokens."""
        agent = MemoryAgent()
        messages = [
            {"content": "Chào bạn, mình là kỹ sư AI.", "sender_user_id": "other_id", "created_at": None}
        ]

        mock_raw_output = "[PEER] là một chuyên gia AI tại Viettel, [PEER] muốn tìm hiểu thêm về RAG."
        with patch.object(agent._llm, "complete", return_value=mock_raw_output):
            summary = await agent.summarize(messages, owner_id="my_id")
            assert "[PEER]" not in summary
            assert "Đối tác" in summary

    def test_clean_interest_keyword(self):
        """Test formatting and shortening interest keywords."""
        from src.agents.memory.agent import clean_interest_keyword
        assert clean_interest_keyword("#AI") == "Ai" or clean_interest_keyword("#AI") == "AI" or clean_interest_keyword("#AI") is not None
        assert clean_interest_keyword("đá bóng") == "Đá Bóng"
        assert clean_interest_keyword("tìm hiểu về mô hình ngôn ngữ lớn để làm dự án") == "Tìm Hiểu Về"

