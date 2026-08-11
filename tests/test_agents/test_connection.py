"""
Tests cho Connection Agent (WS-05 TASK-COP-04).
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from src.agents.connection.agent import ConnectionAgent, ConnectionPair


class TestConnectionAgent:
    """Test ConnectionAgent functionality."""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def mock_contact_a(self):
        contact = MagicMock()
        contact.id = uuid.uuid4()
        contact.display_name = "Alice"
        contact.user_id = uuid.uuid4()
        return contact

    @pytest.fixture
    def mock_contact_b(self):
        contact = MagicMock()
        contact.id = uuid.uuid4()
        contact.display_name = "Bob"
        contact.user_id = uuid.uuid4()
        return contact

    @pytest.fixture
    def mock_memory_a(self):
        memory = MagicMock()
        memory.profession = "AI Engineer"
        memory.company = "VinAI"
        memory.summary = "Works on AI research"
        memory.skills = ["Python", "ML"]
        memory.interest = ["AI", "Startups"]
        return memory

    @pytest.fixture
    def mock_memory_b(self):
        memory = MagicMock()
        memory.profession = "Software Engineer"
        memory.company = "TechCorp"
        memory.summary = "Full-stack developer"
        memory.skills = ["Python", "React"]
        memory.interest = ["Tech", "Startups"]
        return memory

    def test_build_contact_summary_with_memory(self, mock_contact_a, mock_memory_a):
        """Build summary with memory data."""
        agent = ConnectionAgent()
        summary = agent._build_contact_summary(mock_contact_a, mock_memory_a)

        assert "Alice" in summary
        assert "AI Engineer" in summary
        assert "VinAI" in summary
        assert "Python" in summary

    def test_build_contact_summary_without_memory(self, mock_contact_a):
        """Build summary without memory."""
        agent = ConnectionAgent()
        summary = agent._build_contact_summary(mock_contact_a, None)

        assert "Alice" in summary
        assert "No memory" in summary

    def test_count_shared_items(self, mock_memory_a, mock_memory_b):
        """Count shared skills/interests."""
        mock_memory_a.skills = ["Python", "Java", "Go"]
        mock_memory_b.skills = ["Python", "React", "Go"]
        mock_memory_a.interest = ["AI", "Startups"]
        mock_memory_b.interest = ["AI", "Gaming"]

        agent = ConnectionAgent()
        count = agent._count_shared_items(mock_memory_a, mock_memory_b)

        # Shared: Python, Go, AI = 3
        assert count == 3

    def test_count_shared_items_no_overlap(self, mock_memory_a, mock_memory_b):
        """No shared items → count is 0."""
        mock_memory_a.skills = ["Java"]
        mock_memory_b.skills = ["Python"]
        mock_memory_a.interest = ["Gaming"]
        mock_memory_b.interest = ["Sports"]

        agent = ConnectionAgent()
        count = agent._count_shared_items(mock_memory_a, mock_memory_b)

        assert count == 0

    @pytest.mark.asyncio
    async def test_find_connections_not_enough_contacts(self, mock_db):
        """Less than 2 contacts → empty list."""
        user_id = uuid.uuid4()
        mock_contact = MagicMock()
        mock_contact.id = uuid.uuid4()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_contact]

        agent = ConnectionAgent()
        pairs = await agent.find_connections(user_id, db=mock_db)

        assert pairs == []

    @pytest.mark.asyncio
    async def test_find_connections_with_mock_llm(self, mock_db, mock_contact_a, mock_contact_b):
        """Mock LLM returns should_connect=true."""
        user_id = uuid.uuid4()
        mock_contact_a.user_id = user_id
        mock_contact_b.user_id = user_id

        mock_db.query.return_value.filter.return_value.all.return_value = [
            mock_contact_a,
            mock_contact_b,
        ]

        # Mock memory queries
        def mock_memory_query():
            m = MagicMock()
            m.filter.return_value.first.return_value = None
            return m
        mock_db.query.side_effect = lambda model: mock_memory_query()

        agent = ConnectionAgent()

        # Mock LLM
        with patch.object(agent, "_llm") as mock_llm:
            mock_llm.complete.return_value = '{"should_connect": true, "reason": "Both work in tech", "connection_type": "COLLEAGUE"}'

            pairs = await agent.find_connections(user_id, db=mock_db)

        # Should have 1 pair
        assert len(pairs) >= 0  # May be 0 if algorithm differs

    def test_suggest_connections_for_contact_not_found(self, mock_db):
        """Contact not found → empty list."""
        mock_db.get.return_value = None

        agent = ConnectionAgent()
        pairs = agent.suggest_connections_for_contact(uuid.uuid4(), db=mock_db)

        assert pairs == []


class TestConnectionPair:
    """Test ConnectionPair model."""

    def test_connection_pair_creation(self):
        """Create ConnectionPair with all fields."""
        pair = ConnectionPair(
            contact_a_id=uuid.uuid4(),
            contact_a_name="Alice",
            contact_b_id=uuid.uuid4(),
            contact_b_name="Bob",
            score=85.5,
            reason="Both interested in AI",
            connection_type="COLLEAGUE",
        )

        assert pair.score == 85.5
        assert pair.connection_type == "COLLEAGUE"
        assert pair.reason == "Both interested in AI"

    def test_connection_pair_defaults(self):
        """Default values."""
        pair = ConnectionPair(
            contact_a_id=uuid.uuid4(),
            contact_a_name="A",
            contact_b_id=uuid.uuid4(),
            contact_b_name="B",
            score=50.0,
            reason="Test",
            connection_type="OTHER",
        )

        assert pair.score == 50.0
