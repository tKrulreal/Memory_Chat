"""
Tests cho RecommendationWorker.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.events.bus import EventBus
from src.events.types import ChatEvent, EventType
from src.workers.recommendation_worker import RecommendationWorker


class TestRecommendationWorker:
    @pytest.fixture
    def mock_event_bus(self):
        return MagicMock(spec=EventBus)

    @pytest.fixture
    def worker(self, mock_event_bus):
        with patch("src.workers.recommendation_worker.RecommendationAgent"):
            return RecommendationWorker(event_bus=mock_event_bus)

    def test_subscribe_registers_handlers(self, worker, mock_event_bus):
        worker.subscribe()
        mock_event_bus.subscribe.assert_any_call(EventType.MEMORY_UPDATED, worker._handle_trigger)
        mock_event_bus.subscribe.assert_any_call(EventType.SEND_MESSAGE, worker._handle_trigger)

    @pytest.mark.asyncio
    async def test_handle_trigger_generates_recommendations(self, worker):
        user_id = uuid.uuid4()
        event = ChatEvent(
            event_type=EventType.MEMORY_UPDATED,
            user_id=user_id,
            payload={},
            conversation_id=None,
        )

        with patch.object(worker._agent, "generate", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = []

            await worker._handle_trigger(event)

            mock_generate.assert_called_once_with(user_id=user_id)

    @pytest.mark.asyncio
    async def test_handle_trigger_creates_notifications(self, worker):
        user_id = uuid.uuid4()
        event = ChatEvent(
            event_type=EventType.SEND_MESSAGE,
            user_id=user_id,
            payload={},
            conversation_id=None,
        )

        mock_rec = MagicMock()
        mock_rec.type = "PRIORITY"
        mock_rec.priority = "HIGH"

        with patch.object(worker._agent, "generate", new_callable=AsyncMock) as mock_generate, \
             patch("src.workers.recommendation_worker.SessionLocal") as mock_session_local:

            mock_generate.return_value = [mock_rec]

            mock_db = MagicMock()
            mock_session_local.return_value = mock_db

            await worker._handle_trigger(event)

            mock_generate.assert_called_once_with(user_id=user_id)
            # Verify notification was created
            assert mock_db.add.called

    @pytest.mark.asyncio
    async def test_handle_trigger_handles_exception(self, worker):
        user_id = uuid.uuid4()
        event = ChatEvent(
            event_type=EventType.MEMORY_UPDATED,
            user_id=user_id,
            payload={},
            conversation_id=None,
        )

        with patch.object(worker._agent, "generate", new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = Exception("Agent error")

            # Should not raise
            await worker._handle_trigger(event)

            mock_generate.assert_called_once_with(user_id=user_id)

    @pytest.mark.asyncio
    async def test_handle_trigger_calls_generate_with_user_id(self, worker):
        """Test that _handle_trigger passes user_id to generate()."""
        user_id = uuid.uuid4()
        event = ChatEvent(
            event_type=EventType.MEMORY_UPDATED,
            user_id=user_id,
            payload={},
            conversation_id=None,
        )

        with patch.object(worker._agent, "generate", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = []
            await worker._handle_trigger(event)

            # Should call generate with user_id
            mock_generate.assert_called_once_with(user_id=user_id)
