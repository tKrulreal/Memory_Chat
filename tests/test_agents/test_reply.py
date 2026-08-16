"""
Unit tests for ReplySuggestionAgent (AI Smart Reply for Latest Peer Message).
"""

import uuid
from unittest.mock import MagicMock, patch
import pytest

from src.agents.reply.agent import ReplySuggestionAgent
from src.models.chat import Conversation, Message
from src.models.user import User


class TestReplySuggestionAgent:
    """Test ReplySuggestionAgent functionality."""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def agent(self):
        return ReplySuggestionAgent()

    def test_generate_suggested_reply_with_peer_message(self, agent, mock_db):
        """Test generating smart reply when peer sent a message."""
        user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        conv_id = uuid.uuid4()

        conv = Conversation(id=conv_id, user_a_id=user_id, user_b_id=other_user_id)
        other_user = User(id=other_user_id, full_name="Trần Thị Lan", email="lan@gmail.com")

        peer_msg = Message(
            id=uuid.uuid4(),
            conversation_id=conv_id,
            sender_user_id=other_user_id,
            content="Bên bạn có demo giải pháp RAG và tích hợp chatbot không?",
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
            if model == Message:
                # filter chain
                mock_q.filter.return_value.order_by.return_value.first.return_value = peer_msg
                mock_q.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [peer_msg]
            return mock_q

        mock_db.query.side_effect = query_side_effect

        mock_llm_reply = "Chào Lan, bên mình có sẵn demo RAG hoàn chỉnh. Để mình gửi link trải nghiệm cho bạn nhé!"

        with patch.object(agent._llm, "complete", return_value=mock_llm_reply) as mock_complete:
            res = agent.generate_suggested_reply(conv_id, user_id, mock_db)
            assert mock_complete.called
            assert res["peer_name"] == "Trần Thị Lan"
            assert res["peer_last_message"] == "Bên bạn có demo giải pháp RAG và tích hợp chatbot không?"
            assert "Chào Lan" in res["suggested_reply"]

    def test_generate_suggested_reply_without_peer_message(self, agent, mock_db):
        """Test fallback when peer has not sent any message yet."""
        user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        conv_id = uuid.uuid4()

        conv = Conversation(id=conv_id, user_a_id=user_id, user_b_id=other_user_id)
        other_user = User(id=other_user_id, full_name="Lê Văn Hùng", email="hung@gmail.com")

        def get_side_effect(model, ident):
            if model == Conversation:
                return conv
            if model == User:
                return other_user
            return None

        mock_db.get.side_effect = get_side_effect

        def query_side_effect(model):
            mock_q = MagicMock()
            if model == Message:
                mock_q.filter.return_value.order_by.return_value.first.return_value = None
                mock_q.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
            return mock_q

        mock_db.query.side_effect = query_side_effect

        res = agent.generate_suggested_reply(conv_id, user_id, mock_db)
        assert res["peer_name"] == "Lê Văn Hùng"
        assert res["peer_last_message"] is None
        assert "Lê Văn Hùng" in res["suggested_reply"]
