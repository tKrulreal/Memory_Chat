"""
Unit tests for SearchAgent multi-source search.
"""

import json
import uuid
import pytest
from unittest.mock import MagicMock, patch
from src.agents.search.agent import SearchAgent
from src.agents.search.schemas import SearchResult


class TestSearchAgent:
    """Test multi-source search across contacts, tags, summaries, and unchatted profiles."""

    def test_search_result_schema(self):
        """Test SearchResult schema validation."""
        res_chatted = SearchResult(
            conversation_id="conv-123",
            user_id="user-456",
            has_chatted=True,
            name="Nguyễn Văn A",
            email="a@example.com",
            profession="Kỹ sư AI",
            company="FPT",
            skills=["Python", "PyTorch"],
            interests=["AI", "Robot"],
            tags=["Bạn bè", "Khách hàng"],
            score=90,
            explanation="Khớp với từ khóa AI và Robot.",
        )
        assert res_chatted.has_chatted is True
        assert res_chatted.conversation_id == "conv-123"

        res_unchatted = SearchResult(
            conversation_id="",
            user_id="user-789",
            has_chatted=False,
            name="Trần Thị B",
            email="b@example.com",
            profession="Chuyên gia Dữ liệu",
            company="VinAI",
            skills=["BigData"],
            score=85,
            explanation="Người dùng mới có kỹ năng BigData.",
        )
        assert res_unchatted.has_chatted is False
        assert res_unchatted.conversation_id == ""

    def test_search_with_mocked_llm(self):
        """Test SearchAgent.search returns properly structured results."""
        agent = SearchAgent()
        mock_llm_response = json.dumps([
            {
                "conversation_id": "conv-111",
                "user_id": "user-222",
                "has_chatted": True,
                "name": "Lê Văn C",
                "email": "c@example.com",
                "profession": "Robot Engineer",
                "company": "VinFast",
                "skills": ["ROS", "C++"],
                "interests": ["Robot", "Automation"],
                "tags": ["Đối tác"],
                "score": 95,
                "explanation": "Đã từng chat về Robot Automation."
            },
            {
                "conversation_id": "",
                "user_id": "user-333",
                "has_chatted": False,
                "name": "Phạm Thị D",
                "email": "d@example.com",
                "profession": "AI Researcher",
                "company": "Viettel",
                "skills": ["LLM", "NLP"],
                "interests": ["Trí tuệ nhân tạo"],
                "tags": [],
                "score": 88,
                "explanation": "Hồ sơ công khai phù hợp với tìm kiếm LLM."
            }
        ])

        with patch.object(agent.llm, "chat", return_value=mock_llm_response), \
             patch.object(agent.vector_store, "query", return_value={"documents": [], "metadatas": [], "ids": []}), \
             patch("src.agents.search.agent.SessionLocal") as mock_db_cls:
            
            mock_db = MagicMock()
            mock_db_cls.return_value = mock_db

            mock_user = MagicMock()
            mock_user.id = uuid.uuid4()
            mock_user.full_name = "Phạm Thị D"
            mock_user.email = "d@example.com"

            mock_prof = MagicMock()
            mock_prof.profession = "AI Researcher"
            mock_prof.company = "Viettel"
            mock_prof.location = "Hà Nội"
            mock_prof.skills = ["LLM", "NLP"]
            mock_prof.interests = ["AI"]
            mock_prof.bio = "Nghiên cứu AI"
            mock_prof.looking_for = "Đối tác"
            mock_prof.offering = "Kinh nghiệm LLM"

            # Return empty conversations and 1 non-chatted user
            mock_db.query.return_value.filter.return_value.all.return_value = []
            mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = [mock_user]
            mock_db.query.return_value.filter.return_value.first.return_value = mock_prof


            results = agent.search("tìm người làm AI và Robot", str(uuid.uuid4()), limit=5)


            assert len(results) == 2
            assert results[0].has_chatted is True
            assert results[0].name == "Lê Văn C"
            assert results[1].has_chatted is False
            assert results[1].name == "Phạm Thị D"

    def test_search_respects_is_public_flag(self):
        """Test SearchAgent skips non-chatted users who set is_public=False."""
        agent = SearchAgent()
        with patch.object(agent.llm, "chat", return_value="[]"), \
             patch.object(agent.vector_store, "query", return_value={"documents": [], "metadatas": []}), \
             patch("src.agents.search.agent.SessionLocal") as mock_db_cls:

            mock_db = MagicMock()
            mock_db_cls.return_value = mock_db

            # User 1: private profile (is_public=False)
            private_user = MagicMock()
            private_user.id = uuid.uuid4()
            private_user.full_name = "Private User"

            private_prof = MagicMock()
            private_prof.is_public = False

            # Return empty conversations and 1 private non-chatted user
            mock_db.query.return_value.filter.return_value.all.return_value = []
            mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = [private_user]
            mock_db.query.return_value.filter.return_value.first.return_value = private_prof

            results = agent.search("tìm người làm AI", str(uuid.uuid4()), limit=5)
            # Since candidate_pool is empty (private user skipped), results should be empty
            assert results == []
