"""
Unit Tests for TaggingAgent (Contact Category & Profession Tagging).
"""

import uuid
from unittest.mock import MagicMock, patch
import pytest

from src.agents.tagging.agent import TaggingAgent
from src.models.chat import Conversation, Message
from src.models.user import User, UserProfile
from src.models.ai import AssistantMemory


class TestTaggingAgent:
    """Test TaggingAgent functionality."""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def agent(self):
        return TaggingAgent()

    def test_parse_json_response(self, agent):
        """Test parsing valid JSON, markdown block, and invalid strings."""
        # 1. Plain JSON
        raw_json = '{"tags": ["Bạn Bè", "AI Engineer", "Hà Nội"]}'
        parsed = agent._parse_json_response(raw_json)
        assert parsed is not None
        assert parsed["tags"] == ["Bạn Bè", "AI Engineer", "Hà Nội"]

        # 2. Markdown block JSON
        markdown_json = '```json\n{"tags": ["Khách Hàng", "Bất Động Sản"]}\n```'
        parsed = agent._parse_json_response(markdown_json)
        assert parsed is not None
        assert parsed["tags"] == ["Khách Hàng", "Bất Động Sản"]

        # 3. Invalid
        assert agent._parse_json_response("") is None
        assert agent._parse_json_response("No json here") is None

    def test_clean_tags(self, agent):
        """Test filtering out blacklisted junk words, deduplicating, and formatting."""
        raw = [
            "  bạn bè  ",
            "#AI Engineer",
            "chào bạn",      # should be filtered out
            "ok",            # should be filtered out
            "hôm nay",       # should be filtered out
            "AI Engineer",   # duplicate
            "công nghệ",
            "python",
            "flutter",
            "data scientist",
            "extra tag",     # exceeds limit 6
        ]

        cleaned = agent._clean_tags(raw)
        assert "Bạn Bè" in cleaned
        assert "Ai Engineer" in cleaned or "AI Engineer" in [t.upper() for t in cleaned]
        assert "Chào Bạn" not in cleaned
        assert "Ok" not in cleaned
        assert "Hôm Nay" not in cleaned
        assert len(cleaned) <= 6

    def test_generate_tags_from_messages(self, agent, mock_db):
        """Test generating tags from conversation messages using LLM."""
        user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        conv_id = uuid.uuid4()

        conv = Conversation(id=conv_id, user_a_id=user_id, user_b_id=other_user_id)
        other_user = User(id=other_user_id, full_name="Trần Văn Đối Tác", email="doitac@gmail.com")
        other_profile = UserProfile(user_id=other_user_id, profession="CEO", company="TechCorp", location="Hà Nội")

        msg1 = Message(id=uuid.uuid4(), conversation_id=conv_id, sender_user_id=user_id, content="Chào anh, bên em muốn hợp tác dự án AI.")
        msg2 = Message(id=uuid.uuid4(), conversation_id=conv_id, sender_user_id=other_user_id, content="Chào em, anh là CEO TechCorp, bên anh đang cần tìm đối tác triển khai RAG.")

        def get_side_effect(model, ident):
            if model == Conversation:
                return conv
            if model == User:
                return other_user
            return None

        mock_db.get.side_effect = get_side_effect

        def query_side_effect(model):
            mock_q = MagicMock()
            if model == UserProfile:
                mock_q.filter.return_value.first.return_value = other_profile
            elif model == Message:
                mock_q.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [msg1, msg2]
            elif model == AssistantMemory:
                mock_q.filter.return_value.first.return_value = None
            return mock_q

        mock_db.query.side_effect = query_side_effect

        mock_llm_response = '''
        {
            "tags": ["Đối Tác", "CEO", "TechCorp", "AI", "RAG"]
        }
        '''

        with patch.object(agent._llm, "complete", return_value=mock_llm_response) as mock_complete:
            tags = agent.generate_tags(conv_id, user_id, mock_db)
            assert mock_complete.called
            assert "Đối Tác" in tags
            assert "Ceo" in tags or "CEO" in [t.upper() for t in tags]
            assert "Techcorp" in tags or "TechCorp" in [t.upper() for t in tags]

    def test_generate_tags_fallback_to_profile(self, agent, mock_db):
        """Test fallback to UserProfile if no messages exist yet."""
        user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        conv_id = uuid.uuid4()

        conv = Conversation(id=conv_id, user_a_id=user_id, user_b_id=other_user_id)
        other_user = User(id=other_user_id, full_name="Lê Kỹ Sư", email="kysu@gmail.com")
        other_profile = UserProfile(
            user_id=other_user_id,
            profession="Mobile Lead",
            company="FPT Software",
            skills=["Flutter", "Dart"],
        )

        def get_side_effect(model, ident):
            if model == Conversation:
                return conv
            if model == User:
                return other_user
            return None

        mock_db.get.side_effect = get_side_effect

        def query_side_effect(model):
            mock_q = MagicMock()
            if model == UserProfile:
                mock_q.filter.return_value.first.return_value = other_profile
            elif model == Message:
                mock_q.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
            elif model == AssistantMemory:
                mock_q.filter.return_value.first.return_value = None
            return mock_q

        mock_db.query.side_effect = query_side_effect

        tags = agent.generate_tags(conv_id, user_id, mock_db)
        assert len(tags) > 0
        assert "Mobile Lead" in tags
        assert "Fpt Software" in tags
