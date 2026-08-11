"""
Tests cho Tagging Agent (WS-05 TASK-COP-03).
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from src.agents.tagging.agent import TaggingAgent


class TestTaggingAgent:
    """Test TaggingAgent functionality."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def mock_memory(self):
        """Mock ContactMemory."""
        memory = MagicMock()
        memory.summary = "Software engineer at VinAI"
        memory.profession = "AI Engineer"
        memory.company = "VinAI"
        memory.skills = ["Python", "Machine Learning", "Deep Learning"]
        memory.interest = ["AI", "Research", "Startups"]
        memory.timeline = {"last_contact": "2026-08-01"}
        return memory

    def test_build_memory_context(self, mock_memory):
        """Test building readable context from memory."""
        agent = TaggingAgent()
        context = agent._build_memory_context(mock_memory)

        assert "Software engineer" in context
        assert "AI Engineer" in context
        assert "VinAI" in context
        assert "Python" in context

    def test_build_memory_context_empty(self):
        """Test building context from empty memory."""
        agent = TaggingAgent()
        memory = MagicMock()
        memory.summary = None
        memory.profession = None
        memory.company = None
        memory.skills = None
        memory.interest = None
        memory.timeline = None

        context = agent._build_memory_context(memory)
        assert "No memory data" in context

    @pytest.mark.asyncio
    async def test_suggest_tags_no_memory(self, mock_db):
        """No memory → empty list."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        agent = TaggingAgent()
        tags = await agent.suggest_tags(uuid.uuid4(), db=mock_db)
        assert tags == []

    @pytest.mark.asyncio
    async def test_suggest_tags_success(self, mock_db, mock_memory):
        """LLM returns valid tags."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_memory
        agent = TaggingAgent()

        # Mock LLM response
        with patch.object(agent, "_llm") as mock_llm:
            mock_llm.complete.return_value = '["ai_engineer", "software_developer", "vinuni_alumni"]'

            tags = await agent.suggest_tags(uuid.uuid4(), db=mock_db)

        assert len(tags) == 3
        assert "ai_engineer" in tags
        assert "software_developer" in tags
        assert "vinuni_alumni" in tags

    @pytest.mark.asyncio
    async def test_suggest_tags_max_limit(self, mock_db, mock_memory):
        """Tags limited to max_tags."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_memory
        agent = TaggingAgent()

        with patch.object(agent, "_llm") as mock_llm:
            mock_llm.complete.return_value = '["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7"]'

            tags = await agent.suggest_tags(uuid.uuid4(), db=mock_db, max_tags=5)

        assert len(tags) == 5  # Limited to 5

    @pytest.mark.asyncio
    async def test_suggest_tags_invalid_json(self, mock_db, mock_memory):
        """Invalid JSON → empty list."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_memory
        agent = TaggingAgent()

        with patch.object(agent, "_llm") as mock_llm:
            mock_llm.complete.return_value = "Not valid JSON"

            tags = await agent.suggest_tags(uuid.uuid4(), db=mock_db)

        assert tags == []

    @pytest.mark.asyncio
    async def test_suggest_tags_with_markdown(self, mock_db, mock_memory):
        """LLM returns JSON with markdown code block."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_memory
        agent = TaggingAgent()

        with patch.object(agent, "_llm") as mock_llm:
            mock_llm.complete.return_value = '```json\n["tech", "startup"]\n```'

            tags = await agent.suggest_tags(uuid.uuid4(), db=mock_db)

        assert len(tags) == 2
        assert "tech" in tags
        assert "startup" in tags

    def test_get_or_create_tags_existing(self, mock_db):
        """Tag already exists → reuse."""
        existing_tag = MagicMock()
        existing_tag.name = "tech"
        mock_db.query.return_value.filter.return_value.first.return_value = existing_tag

        agent = TaggingAgent()
        tags = agent.get_or_create_tags(mock_db, ["tech"])

        assert len(tags) == 1
        assert tags[0].name == "tech"
        mock_db.add.assert_not_called()  # Should not create new

    def test_get_or_create_tags_new(self, mock_db):
        """Tag doesn't exist → create new."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()

        agent = TaggingAgent()
        tags = agent.get_or_create_tags(mock_db, ["new_tag"])

        assert len(tags) == 1
        assert tags[0].name == "new_tag"
        mock_db.add.assert_called_once()

    def test_get_contact_tags_empty(self, mock_db):
        """Contact has no tags."""
        mock_contact = MagicMock()
        mock_contact.tags = []
        mock_db.get.return_value = mock_contact

        agent = TaggingAgent()
        tags = agent.get_contact_tags(mock_db, uuid.uuid4())

        assert tags == []

    def test_get_contact_tags_with_values(self, mock_db):
        """Contact has tags."""
        tag1 = MagicMock()
        tag1.name = "ai"
        tag2 = MagicMock()
        tag2.name = "tech"

        mock_contact = MagicMock()
        mock_contact.tags = [tag1, tag2]
        mock_db.get.return_value = mock_contact

        agent = TaggingAgent()
        tags = agent.get_contact_tags(mock_db, uuid.uuid4())

        assert len(tags) == 2
        assert "ai" in tags
        assert "tech" in tags

    @pytest.mark.asyncio
    async def test_approve_tags(self, mock_db):
        """Approve tags → added to contact."""
        mock_tag = MagicMock()
        mock_tag.name = "approved_tag"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_tag

        mock_contact = MagicMock()
        mock_contact.tags = []
        mock_db.get.return_value = mock_contact

        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()

        agent = TaggingAgent()
        tags = await agent.approve_tags(mock_db, uuid.uuid4(), ["approved_tag"])

        assert len(tags) == 1
        mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_approve_tags_contact_not_found(self, mock_db):
        """Contact not found → raise ValueError."""
        mock_db.get.return_value = None

        agent = TaggingAgent()
        with pytest.raises(ValueError, match="not found"):
            await agent.approve_tags(mock_db, uuid.uuid4(), ["tag"])
