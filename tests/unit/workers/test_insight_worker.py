"""
Tests cho InsightWorker.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.events.bus import EventBus
from src.events.types import ChatEvent, EventType
from src.workers.insight_worker import InsightWorker


class TestInsightWorker:
    @pytest.fixture
    def mock_event_bus(self):
        return MagicMock(spec=EventBus)

    @pytest.fixture
    def worker(self, mock_event_bus):
        with patch("src.workers.insight_worker.InsightAgent"):
            return InsightWorker(event_bus=mock_event_bus)

    def test_start_registers_handlers(self, worker, mock_event_bus):
        worker.start()
        mock_event_bus.subscribe.assert_called_once_with(
            EventType.MEMORY_UPDATED, worker._handle_memory_updated
        )

    @pytest.mark.asyncio
    async def test_handle_memory_updated_extracts_contact_id(self, worker):
        contact_id = uuid.uuid4()
        event = ChatEvent(
            event_type=EventType.MEMORY_UPDATED,
            user_id=uuid.uuid4(),
            payload={"contact_id": str(contact_id)},
            conversation_id=None,
        )

        with patch.object(worker._agent, "generate_insights", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = []

            await worker._handle_memory_updated(event)

            # Worker should convert string to UUID
            mock_generate.assert_called_once_with(contact_id=contact_id)

    @pytest.mark.asyncio
    async def test_handle_memory_updated_skips_if_no_contact_id(self, worker):
        event = ChatEvent(
            event_type=EventType.MEMORY_UPDATED,
            user_id=uuid.uuid4(),
            payload={},  # No contact_id
            conversation_id=None,
        )

        with patch.object(worker._agent, "generate_insights", new_callable=AsyncMock) as mock_generate:
            await worker._handle_memory_updated(event)

            # Should not call generate_insights if no contact_id
            mock_generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_memory_updated_handles_exception(self, worker):
        contact_id = uuid.uuid4()
        event = ChatEvent(
            event_type=EventType.MEMORY_UPDATED,
            user_id=uuid.uuid4(),
            payload={"contact_id": str(contact_id)},
            conversation_id=None,
        )

        with patch.object(worker._agent, "generate_insights", new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = Exception("Agent error")

            # Should not raise
            await worker._handle_memory_updated(event)

            mock_generate.assert_called_once_with(contact_id=contact_id)

    @pytest.mark.asyncio
    async def test_handle_memory_updated_logs_insights_count(self, worker):
        contact_id = uuid.uuid4()
        event = ChatEvent(
            event_type=EventType.MEMORY_UPDATED,
            user_id=uuid.uuid4(),
            payload={"contact_id": str(contact_id)},
            conversation_id=None,
        )

        mock_insight = MagicMock()
        mock_insight.type = "INTEREST_PATTERN"
        mock_insight.description = "Likes AI topics"

        with patch.object(worker._agent, "generate_insights", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = [mock_insight]

            await worker._handle_memory_updated(event)

            mock_generate.assert_called_once_with(contact_id=contact_id)
