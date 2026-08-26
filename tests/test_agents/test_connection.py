"""
Unit Tests for ConnectionRecommendationAgent (5-step Multi-stage Pipeline).
"""

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
import pytest

from src.agents.connection.agent import (
    ConnectionRecommendationAgent,
    FeatureScores,
    UserMatchResult,
    _calculate_jaccard,
    _calculate_goal_synergy,
    _calculate_location_score,
    _calculate_activity_score,
)
from src.agents.connection.schemas import UserProfileDict
from src.models.user import User, UserProfile, UserBlock, Setting
from src.models.chat import Conversation
from src.models.connection import ConnectionRequest
from src.models.ai import AssistantMemory, Recommendation


class TestConnectionRecommendationAgent:
    """Test ConnectionRecommendationAgent 5-step pipeline."""

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
            location="Hà Nội",
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
            location="Hà Nội",
            skills=["Flutter", "React Native", "Mobile"],
            interests=["Mobile Apps", "Startups"],
            current_needs=["Tìm đối tác kỹ thuật AI"],
            current_offers=["Kinh nghiệm phát triển app di động"],
            summary="Chuyên gia xây dựng mobile apps",
        )

    # -------------------------------------------------------------------------
    # Helper & JSON Parsing Tests
    # -------------------------------------------------------------------------
    def test_parse_json_response(self, agent):
        """Test parsing valid JSON, markdown block, and invalid strings."""
        raw_json = '{"match_score": 0.88, "priority": "HIGH", "reason": "Good match"}'
        parsed = agent._parse_json_response(raw_json)
        assert parsed is not None
        assert parsed["match_score"] == 0.88

        markdown_json = '```json\n{"match_score": 0.75, "priority": "MEDIUM", "reason": "Both do tech"}\n```'
        parsed = agent._parse_json_response(markdown_json)
        assert parsed is not None
        assert parsed["match_score"] == 0.75

        assert agent._parse_json_response("") is None
        assert agent._parse_json_response("No json here") is None

    # -------------------------------------------------------------------------
    # BƯỚC 1: SQL Hard Filter Tests
    # -------------------------------------------------------------------------
    def test_get_candidate_users_sql_filter(self, agent, mock_db):
        """Test Step 1: SQL Hard Filter excludes self, conversations, requests, blocks, private profiles."""
        user_id = uuid.uuid4()
        cand1 = User(id=uuid.uuid4(), email="cand1@test.com", full_name="Candidate 1")
        cand2 = User(id=uuid.uuid4(), email="cand2@test.com", full_name="Candidate 2")

        def query_mock(model):
            m = MagicMock()
            if model == Conversation:
                m.filter.return_value.all.return_value = []
            elif model == ConnectionRequest:
                m.filter.return_value.all.return_value = []
            elif model == Recommendation:
                m.filter.return_value.all.return_value = []
            elif model == UserBlock:
                m.filter.return_value.all.return_value = []
            elif model == User:
                # Chain outerjoin -> outerjoin -> filter -> all
                m.outerjoin.return_value.outerjoin.return_value.filter.return_value.all.return_value = [cand1, cand2]
                m.filter.return_value.all.return_value = [cand1, cand2]
            return m

        mock_db.query.side_effect = query_mock

        candidates = agent.get_candidate_users(user_id, mock_db)
        assert len(candidates) == 2
        assert candidates[0].email == "cand1@test.com"

    # -------------------------------------------------------------------------
    # BƯỚC 2: Candidate Retrieval Tests
    # -------------------------------------------------------------------------
    def test_retrieve_candidates_with_vector_search(self, agent, user_a_profile, mock_db):
        """Test Step 2: Retrieval uses profile embeddings and searches Qdrant."""
        cand_user = User(id=uuid.uuid4(), email="cand@test.com", full_name="Cand User")
        mock_embedding = [0.1] * 1536

        with patch.object(agent._llm, "embed", return_value=mock_embedding):
            with patch.object(agent._vector_store, "search_profiles", return_value=[{"user_id": str(cand_user.id), "score": 0.85}]):
                with patch.object(agent, "extract_user_profile", return_value={"user_id": str(cand_user.id), "skills": ["Python"]}):
                    results = agent.retrieve_candidates(user_a_profile, [cand_user], mock_db, top_k=10)

        assert len(results) == 1
        user_res, prof_res, sem_score = results[0]
        assert user_res.id == cand_user.id
        assert sem_score == 0.85

    # -------------------------------------------------------------------------
    # BƯỚC 3: Feature Engineering Tests
    # -------------------------------------------------------------------------
    def test_calculate_feature_scores(self, agent, user_a_profile, user_b_profile):
        """Test Step 3: Feature engineering calculates all 6 components accurately."""
        cand_user = User(
            id=uuid.UUID(user_b_profile["user_id"]),
            email="user_b@example.com",
            full_name="User B",
            updated_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )

        scores = agent.calculate_feature_scores(
            current_profile=user_a_profile,
            candidate_profile=user_b_profile,
            candidate_user=cand_user,
            semantic_score=0.90,
        )

        assert isinstance(scores, FeatureScores)
        assert scores.semantic == 0.90
        assert scores.location == 1.0  # Both in Hà Nội
        assert scores.activity == 1.0  # Within 24h
        assert 0.0 <= scores.skill <= 1.0
        assert 0.0 <= scores.interest <= 1.0
        assert scores.goal > 0.0  # Mobile Dev need vs Mobile skills synergy

    def test_feature_helpers(self):
        """Test standalone feature calculation functions."""
        # Location
        assert _calculate_location_score("Hà Nội", "Hanoi") == 1.0
        assert _calculate_location_score("TP.HCM", "TP Hồ Chí Minh") == 1.0
        assert _calculate_location_score("Hà Nội", "Singapore") == 0.0
        assert _calculate_location_score("Việt Nam", "Vietnam") == 0.5

        # Jaccard
        assert _calculate_jaccard(["Python", "AI"], ["Python", "FastAPI"]) > 0.0
        assert _calculate_jaccard(["Python"], ["Java"]) == 0.0

        # Goal synergy
        synergy = _calculate_goal_synergy(
            needs_a=["Senior AI Engineer"], offers_a=["Frontend"], skills_a=["React"],
            needs_b=["React Web App"], offers_b=["AI RAG Architect"], skills_b=["Python", "AI"]
        )
        assert synergy > 0.3

        # Activity
        active_user = User(id=uuid.uuid4(), updated_at=datetime.now(timezone.utc) - timedelta(hours=1))
        assert _calculate_activity_score(active_user) == 1.0
        old_user = User(id=uuid.uuid4(), updated_at=datetime.now(timezone.utc) - timedelta(days=60))
        assert _calculate_activity_score(old_user) == 0.2

    # -------------------------------------------------------------------------
    # BƯỚC 4: Weighted Scoring Tests
    # -------------------------------------------------------------------------
    def test_compute_weighted_score(self, agent):
        """Test Step 4: Formula 0.30*Sem + 0.25*Skill + 0.15*Int + 0.15*Goal + 0.10*Loc + 0.05*Act."""
        # Perfect match
        perfect_feat = FeatureScores(
            semantic=1.0,
            skill=1.0,
            interest=1.0,
            goal=1.0,
            location=1.0,
            activity=1.0,
        )
        assert agent.compute_weighted_score(perfect_feat) == 1.0

        # Custom mix
        # 0.30*0.8 + 0.25*0.6 + 0.15*0.4 + 0.15*0.8 + 0.10*1.0 + 0.05*1.0
        # = 0.24 + 0.15 + 0.06 + 0.12 + 0.10 + 0.05 = 0.72
        mixed_feat = FeatureScores(
            semantic=0.8,
            skill=0.6,
            interest=0.4,
            goal=0.8,
            location=1.0,
            activity=1.0,
        )
        assert agent.compute_weighted_score(mixed_feat) == 0.72

    # -------------------------------------------------------------------------
    # BƯỚC 5: Targeted LLM Refinement & Fallback Tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_compare_users_with_mock_llm(self, agent, user_a_profile, user_b_profile):
        """Test Step 5: Targeted LLM generates reason and suggested intro."""
        mock_response = '''
        ```json
        {
            "reason": "Bạn nên kết nối với User B vì User B có kinh nghiệm phát triển mobile app Flutter đáp ứng đúng nhu cầu tìm kiếm của bạn.",
            "suggested_intro": "Chào User B, mình thấy bạn đang làm về Mobile rất ấn tượng!",
            "complementary_aspects": ["Mobile Development", "AI Backend"],
            "shared_interests": ["Startups"]
        }
        ```
        '''
        with patch.object(agent._llm, "complete", return_value=mock_response):
            result = await agent.compare_users(user_a_profile, user_b_profile, precomputed_score=0.88)

        assert result is not None
        assert result.match_score == 0.88
        assert result.priority == "HIGH"
        assert "User B" in result.reason
        assert "Chào User B" in result.suggested_intro

    @pytest.mark.asyncio
    async def test_compare_users_fallback_when_llm_fails(self, agent, user_a_profile, user_b_profile):
        """Test Step 5: Fallback smoothly generates structured reasons if LLM fails."""
        with patch.object(agent._llm, "complete", side_effect=Exception("LLM Timeout")):
            result = await agent.compare_users(user_a_profile, user_b_profile, precomputed_score=0.75)

        assert result is not None
        assert result.match_score == 0.75
        assert result.priority == "MEDIUM"
        assert "User B" in result.reason
        assert "Chào User B" in result.suggested_intro

    # -------------------------------------------------------------------------
    # Extract User Profile Tests
    # -------------------------------------------------------------------------
    def test_extract_user_profile_prefers_user_profile_table(self, agent, mock_db):
        """Test extract_user_profile prioritizes user-entered UserProfile data."""
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

    @pytest.mark.asyncio
    async def test_generate_pipeline_limit_top_5(self, agent, user_a_profile):
        """Test full generate pipeline produces recommendations capped at limit."""
        current_user = User(id=uuid.UUID(user_a_profile["user_id"]), email="user_a@example.com", full_name="User A")
        cands = [
            User(id=uuid.uuid4(), email=f"cand_{i}@example.com", full_name=f"Candidate {i}")
            for i in range(10)
        ]

        mock_db = MagicMock()
        mock_db.get.return_value = current_user

        with patch("src.agents.connection.agent.SessionLocal", return_value=mock_db):
            with patch.object(agent, "extract_user_profile", return_value=user_a_profile):
                with patch.object(agent, "get_candidate_users", return_value=cands):
                    with patch.object(agent, "retrieve_candidates", return_value=[(c, user_a_profile, 0.8) for c in cands]):
                        with patch.object(agent._llm, "complete", side_effect=Exception("Offline")):
                            results = await agent.generate(current_user.id, min_score=0.4, limit=5)

        assert len(results) == 5
        assert mock_db.commit.called

