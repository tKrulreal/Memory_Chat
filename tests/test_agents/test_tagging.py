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

    def test_generate_tags_no_user_tags_returns_empty(self, agent, mock_db):
        """When user has no tags configured in AI Hub, generate_tags must return []."""
        user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        conv_id = uuid.uuid4()

        conv = Conversation(id=conv_id, user_a_id=user_id, user_b_id=other_user_id)
        other_user = User(id=other_user_id, full_name="Trần Văn Đối Tác", email="doitac@gmail.com")

        mock_db.get.side_effect = lambda model, ident: conv if model == Conversation else (other_user if model == User else None)

        from src.models.tag import Tag
        def query_side_effect(model):
            mock_q = MagicMock()
            if model == Tag:
                mock_q.filter.return_value.all.return_value = [] # No tags configured
            elif model == AssistantMemory:
                mock_q.filter.return_value.first.return_value = None
            return mock_q

        mock_db.query.side_effect = query_side_effect

        with patch.object(agent._llm, "complete") as mock_complete:
            tags = agent.generate_tags(conv_id, user_id, mock_db)
            assert tags == []
            assert not mock_complete.called

    def test_generate_tags_strict_whitelist_from_ai_hub(self, agent, mock_db):
        """Test that generated tags are strictly filtered to only match user's AI Hub tags."""
        user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        conv_id = uuid.uuid4()

        conv = Conversation(id=conv_id, user_a_id=user_id, user_b_id=other_user_id)
        other_user = User(id=other_user_id, full_name="Trần Văn Đối Tác", email="doitac@gmail.com")
        other_profile = UserProfile(user_id=other_user_id, profession="CEO", company="TechCorp", location="Hà Nội")

        msg1 = Message(id=uuid.uuid4(), conversation_id=conv_id, sender_user_id=user_id, content="Chào anh, bên em muốn hợp tác dự án AI.")
        msg2 = Message(id=uuid.uuid4(), conversation_id=conv_id, sender_user_id=other_user_id, content="Chào em, anh là CEO TechCorp.")

        from src.models.tag import Tag
        tag1 = Tag(user_id=user_id, name="Đối Tác", is_active=True)
        tag2 = Tag(user_id=user_id, name="CEO", is_active=True)
        tag3 = Tag(user_id=user_id, name="Khách Hàng", is_active=True)

        def get_side_effect(model, ident):
            if model == Conversation:
                return conv
            if model == User:
                return other_user
            return None

        mock_db.get.side_effect = get_side_effect

        def query_side_effect(model):
            mock_q = MagicMock()
            if model == Tag:
                mock_q.filter.return_value.all.return_value = [tag1, tag2, tag3]
            elif model == UserProfile:
                mock_q.filter.return_value.first.return_value = other_profile
            elif model == Message:
                mock_q.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [msg1, msg2]
            elif model == AssistantMemory:
                mock_q.filter.return_value.first.return_value = None
            return mock_q

        mock_db.query.side_effect = query_side_effect

        # LLM returns some matched and some non-whitelisted tags ("RandomTag", "Hà Nội")
        mock_llm_response = '''
        {
            "tags": ["Đối Tác", "CEO", "RandomTag", "Hà Nội"]
        }
        '''

        with patch.object(agent._llm, "complete", return_value=mock_llm_response) as mock_complete:
            tags = agent.generate_tags(conv_id, user_id, mock_db)
            assert mock_complete.called
            # Only whitelisted tags in AI Hub are kept
            assert "Đối Tác" in tags
            assert "CEO" in tags
            assert "RandomTag" not in tags
            assert "Hà Nội" not in tags
