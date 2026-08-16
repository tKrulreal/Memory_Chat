"""
Unit Tests for ConnectionRecommendationAgent (User-to-User Networking).
"""

import uuid
from unittest.mock import MagicMock, patch
import pytest

from src.agents.connection.agent import (
    ConnectionRecommendationAgent,
    UserMatchResult,
)
from src.agents.connection.schemas import UserProfileDict
from src.models.user import User
from src.models.ai import AssistantMemory, Recommendation


class TestConnectionRecommendationAgent:
    """Test ConnectionRecommendationAgent functionality."""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def agent(self):
        return ConnectionRecommendationAgent()

    @pytest.fixture
    def user_a_profile(self) -> UserProfileDict:
        return UserProfileDict(
            user_id=str(uuid.uuid4()),
            email="user_a@example.com",
            full_name="User A",
            avatar=None,
            profession="Tech Lead",
            company="Company A",
            skills=["Python", "AI", "FastAPI"],
            interests=["Generative AI", "Startups"],
            current_needs=["Tìm Senior Mobile Developer"],
            current_offers=["Kinh nghiệm RAG và LLM Agents"],
            summary="Thích công nghệ và phát triển sản phẩm",
        )

    @pytest.fixture
    def user_b_profile(self) -> UserProfileDict:
        return UserProfileDict(
            user_id=str(uuid.uuid4()),
            email="user_b@example.com",
            full_name="User B",
            avatar=None,
            profession="Mobile Developer",
            company="Company B",
            skills=["Flutter", "React Native", "Mobile"],
            interests=["Mobile Apps", "Startups"],
            current_needs=["Tìm đối tác kỹ thuật AI"],
            current_offers=["Kinh nghiệm phát triển app di động"],
            summary="Chuyên gia xây dựng mobile apps",
        )

    def test_parse_json_response(self, agent):
        """Test parsing valid JSON, markdown block, and invalid strings."""
        # 1. Plain JSON
        raw_json = '{"match_score": 0.88, "priority": "HIGH", "reason": "Good match"}'
        parsed = agent._parse_json_response(raw_json)
        assert parsed is not None
        assert parsed["match_score"] == 0.88

        # 2. Markdown block JSON
        markdown_json = '```json\n{"match_score": 0.75, "priority": "MEDIUM", "reason": "Both do tech"}\n```'
        parsed = agent._parse_json_response(markdown_json)
        assert parsed is not None
        assert parsed["match_score"] == 0.75

        # 3. Invalid
        assert agent._parse_json_response("") is None
        assert agent._parse_json_response("No json here") is None

    @pytest.mark.asyncio
    async def test_compare_users_with_mock_llm(self, agent, user_a_profile, user_b_profile):
        """Test compare_users parsing LLM response accurately."""
        mock_response = '''
        ```json
        {
            "match_score": 0.92,
            "priority": "HIGH",
            "reason": "User A cần Mobile Dev trong khi User B là chuyên gia Flutter/React Native.",
            "suggested_intro": "Chào User B, mình thấy bạn làm về Mobile rất ấn tượng!",
            "complementary_aspects": ["Mobile Development", "AI Backend"],
            "shared_interests": ["Startups"]
        }
        ```
        '''
        with patch.object(agent._llm, "complete", return_value=mock_response):
            result = await agent.compare_users(user_a_profile, user_b_profile)

        assert result is not None
        assert result.match_score == 0.92
        assert result.priority == "HIGH"
        assert "Mobile Dev" in result.reason
        assert "User B" in result.suggested_intro

    @pytest.mark.asyncio
    async def test_compare_users_dynamic_fallback(self, agent, user_a_profile, user_b_profile):
        """Test fallback calculation if LLM raises exception."""
        with patch.object(agent._llm, "complete", side_effect=Exception("API Timeout")):
            result = await agent.compare_users(user_a_profile, user_b_profile)

        assert result is not None
        assert 0.5 <= result.match_score <= 1.0
        assert result.priority in ["HIGH", "MEDIUM", "LOW"]
        assert "User B" in result.reason

    def test_get_candidate_users(self, agent, mock_db):
        """Test getting candidates excludes self and already connected users."""
        user_id = uuid.uuid4()
        cand1 = User(id=uuid.uuid4(), email="cand1@test.com", full_name="Candidate 1")
        cand2 = User(id=uuid.uuid4(), email="cand2@test.com", full_name="Candidate 2")

        # mock conversations query
        mock_db.query.return_value.filter.return_value.all.side_effect = [
            [], # existing convs
            [], # existing recs
            [cand1, cand2], # candidate users query
        ]

        candidates = agent.get_candidate_users(user_id, mock_db)
        assert len(candidates) == 2

    def test_extract_user_profile_prefers_user_profile_table(self, agent, mock_db):
        """Test extract_user_profile prioritizes user-entered UserProfile data."""
        from src.models.user import UserProfile
        user = User(id=uuid.uuid4(), email="lead@test.com", full_name="Manual User")
        profile = UserProfile(
            user_id=user.id,
            profession="Senior Architect",
            company="Enterprise Corp",
            location="Hà Nội",
            skills=["Kubernetes", "Golang"],
            interests=["Cloud", "DevOps"],
            looking_for=["Tìm DevOps Lead"],
            offering=["Tư vấn hạ tầng đám mây"],
        )

        mock_db.query.return_value.filter.return_value.first.return_value = profile
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.all.return_value = []

        extracted = agent.extract_user_profile(user, mock_db)
        assert extracted["profession"] == "Senior Architect"
        assert extracted["company"] == "Enterprise Corp"
        assert extracted["location"] == "Hà Nội"
        assert "Kubernetes" in extracted["skills"]
        assert "Cloud" in extracted["interests"]
        assert "Tìm DevOps Lead" in extracted["current_needs"]
        assert "Tư vấn hạ tầng đám mây" in extracted["current_offers"]

    def test_extract_user_profile_falls_back_to_assistant_memory(self, agent, mock_db):
        """Test extract_user_profile falls back to chat memories if UserProfile not set."""
        user = User(id=uuid.uuid4(), email="chatuser@test.com", full_name="Chat User")
        memory = AssistantMemory(
            id=uuid.uuid4(),
            owner_user_id=user.id,
            conversation_id=uuid.uuid4(),
            summary="Thích Python và AI",
            facts={
                "profession": "AI Researcher",
                "company": "AI Lab",
                "location": "TP. Hồ Chí Minh",
                "skills": ["PyTorch", "NLP"],
                "interests": ["Deep Learning"],
                "looking_for": ["Tìm compute GPU"],
                "offering": ["Huấn luyện model"],
            }
        )

        from src.models.user import UserProfile
        from src.models.chat import Message
        from src.models.contact import Contact

        def query_side_effect(model):
            mock_q = MagicMock()
            if model == UserProfile:
                mock_q.filter.return_value.first.return_value = None
            elif model == AssistantMemory:
                mock_q.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [memory]
                mock_q.filter.return_value.all.return_value = [memory]
            elif model == Message:
                mock_q.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
                mock_q.filter.return_value.all.return_value = []
            elif model == Contact:
                mock_q.filter.return_value.first.return_value = None
            return mock_q

        mock_db.query.side_effect = query_side_effect

        extracted = agent.extract_user_profile(user, mock_db)
        assert extracted["profession"] == "AI Researcher"
        assert extracted["company"] == "AI Lab"
        assert extracted["location"] == "TP. Hồ Chí Minh"
        assert "PyTorch" in extracted["skills"]
        assert "Deep Learning" in extracted["interests"]
        assert "Tìm compute GPU" in extracted["current_needs"]
        assert "Huấn luyện model" in extracted["current_offers"]


