"""
Unit tests for MemoryAgent and Peer Isolation / Sanitization.
"""

import json
import uuid
import pytest
from unittest.mock import MagicMock, patch
from src.agents.memory.agent import MemoryAgent, sanitize_peer_text, clean_interest_keyword


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
        assert clean_interest_keyword("#AI") in ["AI", "Ai"]
        assert clean_interest_keyword("đá bóng") == "Đá Bóng"
        assert clean_interest_keyword("tìm hiểu về mô hình ngôn ngữ lớn để làm dự án") == "Tìm Hiểu Về"

    @pytest.mark.asyncio
    async def test_extract_entities_free_form_and_latest_follow_up(self):
        """Test entity extraction extracts free-form topics and latest follow-up."""
        agent = MemoryAgent()
        messages = [
            {"content": "Mình là lập trình viên.", "sender_user_id": "other_id", "created_at": None},
            {"content": "Gửi cho mình tài liệu RAG nhé!", "sender_user_id": "other_id", "created_at": None}
        ]

        mock_json_response = json.dumps({
            "last_met": "Trao đổi qua tin nhắn tuần này",
            "interested_in": ["Trí Tuệ Nhân Tạo", "RAG Pipeline", "Đầu Tư Khởi Nghiệp"],
            "follow_up": "Gửi tài liệu kỹ thuật RAG cho đối tác."
        })

        with patch.object(agent._llm, "complete", return_value=mock_json_response):
            entities = await agent.extract_entities(messages, owner_id="my_id")
            assert len(entities["interested_in"]) == 3
            assert "RAG Pipeline" in entities["interested_in"] or "Rag Pipeline" in entities["interested_in"]
            assert entities["follow_up"] == "Gửi tài liệu kỹ thuật RAG cho đối tác."
            assert entities["last_met"] == "Trao đổi qua tin nhắn tuần này"

    @pytest.mark.asyncio
    async def test_build_memory_independent_of_ai_hub_tag_limit(self):
        """Test build_memory does not cap interested_in by AI Hub tag_limit setting."""
        agent = MemoryAgent()
        messages = [
            {"content": "Chào bạn, mình làm về Deep Learning và Robotics.", "sender_user_id": "other_id", "created_at": None}
        ]

        mock_summary = "Đối tác là kỹ sư nghiên cứu Deep Learning và Robotics."
        mock_entities = {
            "last_met": "Hôm nay",
            "interested_in": ["Deep Learning", "Robotics", "Computer Vision", "AI Agents", "Python"],
            "follow_up": "Thảo luận thêm về ứng dụng AI Agents."
        }

        with patch.object(agent, "summarize", return_value=mock_summary), \
             patch.object(agent, "extract_entities", return_value=mock_entities):
            
            # Simulated db mock with AI Hub config having tag_limit=2 (which is ONLY for tagging)
            mock_db = MagicMock()
            mock_setting = MagicMock()
            mock_setting.ai_memory_window = "unlimited"
            mock_db.query.return_value.filter.return_value.first.return_value = mock_setting

            res = await agent.build_memory(
                user_id=uuid.uuid4(),
                conversation_id=uuid.uuid4(),
                messages=messages,
                db=mock_db,
            )

            # All 5 interests should be preserved in interested_in (not truncated by tag_limit=2)
            assert len(res.interested_in) == 5
            assert "Robotics" in res.interested_in
            assert res.summary == mock_summary
            assert res.follow_up == "Thảo luận thêm về ứng dụng AI Agents."
