"""
Tests cho MemoryWorker.
"""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from src.events.bus import EventBus
from src.events.types import ChatEvent, EventType
from src.workers.memory_worker import MemoryWorker


class TestMemoryWorker:
    @pytest.fixture
    def mock_session_factory(self):
        session = MagicMock()
        session.query.return_value.filter.return_value.first.return_value = None
        return MagicMock(return_value=session)

    @pytest.fixture
    def mock_event_bus(self):
        bus = MagicMock(spec=EventBus)
        return bus

    @pytest.fixture
    def worker(self, mock_event_bus, mock_session_factory):
        return MemoryWorker(
            event_bus=mock_event_bus,
            session_factory=mock_session_factory,
        )

    def test_subscribe_registers_handlers(self, worker, mock_event_bus):
        worker.subscribe()
        mock_event_bus.subscribe.assert_any_call(EventType.SEND_MESSAGE, worker._on_send_message)
        mock_event_bus.subscribe.assert_any_call(EventType.CLOSE_CHAT, worker._on_close_chat)
        mock_event_bus.subscribe.assert_any_call(EventType.OPEN_AI, worker._on_open_ai)

    def test_on_open_ai_extracts_contact_id(self, worker):
        event = ChatEvent(
            event_type=EventType.OPEN_AI,
            user_id=uuid.uuid4(),
            payload={"contact_id": str(uuid.uuid4())},
            conversation_id=None,
        )

        # Mock _queue_refresh
        worker._queue_refresh = AsyncMock()

        # Run sync (on_open_ai is async)
        asyncio.get_event_loop().run_until_complete(worker._on_open_ai(event))
        worker._queue_refresh.assert_called_once()

    def test_on_send_message_skips_if_no_conversation(self, worker, mock_session_factory):
        session = mock_session_factory.return_value
        session.query.return_value.filter.return_value.first.return_value = None

        event = ChatEvent(
            event_type=EventType.SEND_MESSAGE,
            user_id=uuid.uuid4(),
            payload={"message_id": str(uuid.uuid4())},
            conversation_id=uuid.uuid4(),
        )

        worker._queue_refresh = AsyncMock()
        asyncio.get_event_loop().run_until_complete(worker._on_send_message(event))
        worker._queue_refresh.assert_not_called()

    def test_on_close_chat_skips_if_no_conversation(self, worker, mock_session_factory):
        session = mock_session_factory.return_value
        session.query.return_value.filter.return_value.first.return_value = None

        event = ChatEvent(
            event_type=EventType.CLOSE_CHAT,
            user_id=uuid.uuid4(),
            payload={},
            conversation_id=uuid.uuid4(),
        )

        worker._queue_refresh = AsyncMock()
        asyncio.get_event_loop().run_until_complete(worker._on_close_chat(event))
        worker._queue_refresh.assert_not_called()

    def test_on_send_message_triggers_when_idle(
        self, worker, mock_session_factory
    ):
        # Create a conversation that's idle > 5 minutes
        contact_id = uuid.uuid4()
        conversation = MagicMock()
        conversation.contact_id = contact_id
        conversation.last_message_time = datetime.now(timezone.utc) - timedelta(minutes=10)

        session = mock_session_factory.return_value
        session.query.return_value.filter.return_value.first.return_value = conversation

        event = ChatEvent(
            event_type=EventType.SEND_MESSAGE,
            user_id=uuid.uuid4(),
            payload={},
            conversation_id=uuid.uuid4(),
        )

        worker._queue_refresh = AsyncMock()
        asyncio.get_event_loop().run_until_complete(worker._on_send_message(event))
        worker._queue_refresh.assert_called_once_with(contact_id)

    def test_on_send_message_skips_if_recent(
        self, worker, mock_session_factory
    ):
        # Conversation has message < 5 minutes ago
        conversation = MagicMock()
        conversation.contact_id = uuid.uuid4()
        conversation.last_message_time = datetime.now(timezone.utc) - timedelta(minutes=1)

        session = mock_session_factory.return_value
        session.query.return_value.filter.return_value.first.return_value = conversation

        event = ChatEvent(
            event_type=EventType.SEND_MESSAGE,
            user_id=uuid.uuid4(),
            payload={},
            conversation_id=uuid.uuid4(),
        )

        worker._queue_refresh = AsyncMock()
        asyncio.get_event_loop().run_until_complete(worker._on_send_message(event))
        # Should not trigger since it's recent
        worker._queue_refresh.assert_not_called()

    def test_on_close_chat_triggers(
        self, worker, mock_session_factory
    ):
        contact_id = uuid.uuid4()
        conversation = MagicMock()
        conversation.contact_id = contact_id

        session = mock_session_factory.return_value
        session.query.return_value.filter.return_value.first.return_value = conversation

        event = ChatEvent(
            event_type=EventType.CLOSE_CHAT,
            user_id=uuid.uuid4(),
            payload={},
            conversation_id=uuid.uuid4(),
        )

        worker._queue_refresh = AsyncMock()
        asyncio.get_event_loop().run_until_complete(worker._on_close_chat(event))
        worker._queue_refresh.assert_called_once_with(contact_id)
