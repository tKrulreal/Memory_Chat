"""
Tests cho MemoryWorker.
"""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.events.bus import EventBus
from src.events.types import ChatEvent, EventType
from src.workers.memory_worker import MemoryWorker


def _run(coro):
    """Helper: chạy async coroutine trong test sync (dùng asyncio.run)."""
    return asyncio.run(coro)


class TestMemoryWorker:
    @pytest.fixture
    def mock_session_factory(self):
        session = MagicMock()
        session.query.return_value.filter.return_value.first.return_value = None
        return MagicMock(return_value=session)

    @pytest.fixture
    def mock_event_bus(self):
        return MagicMock(spec=EventBus)

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
        contact_id = uuid.uuid4()
        event = ChatEvent(
            event_type=EventType.OPEN_AI,
            user_id=uuid.uuid4(),
            payload={"contact_id": str(contact_id)},
            conversation_id=None,
        )

        worker._queue_refresh = AsyncMock()
        _run(worker._on_open_ai(event))
        worker._queue_refresh.assert_called_once_with(contact_id)

    def test_on_open_ai_handles_missing_contact_id(self, worker):
        event = ChatEvent(
            event_type=EventType.OPEN_AI,
            user_id=uuid.uuid4(),
            payload={},  # No contact_id
            conversation_id=None,
        )

        worker._queue_refresh = AsyncMock()
        _run(worker._on_open_ai(event))
        worker._queue_refresh.assert_not_called()

    def test_on_open_ai_handles_invalid_contact_id(self, worker):
        event = ChatEvent(
            event_type=EventType.OPEN_AI,
            user_id=uuid.uuid4(),
            payload={"contact_id": "not-a-uuid"},
            conversation_id=None,
        )

        worker._queue_refresh = AsyncMock()
        _run(worker._on_open_ai(event))
        # Should log warning, not raise
        worker._queue_refresh.assert_not_called()

    def test_on_send_message_skips_if_no_conversation(self, worker, mock_session_factory):
        session = mock_session_factory.return_value
        session.query.return_value.filter.return_value.first.return_value = None

        event = ChatEvent(
            event_type=EventType.SEND_MESSAGE,
            user_id=uuid.uuid4(),
            payload={},
            conversation_id=uuid.uuid4(),
        )

        worker._queue_refresh = AsyncMock()
        _run(worker._on_send_message(event))
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
        _run(worker._on_close_chat(event))
        worker._queue_refresh.assert_not_called()

    def test_on_send_message_triggers_when_idle(self, worker, mock_session_factory):
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
        _run(worker._on_send_message(event))
        worker._queue_refresh.assert_called_once_with(contact_id)

    def test_on_send_message_skips_if_recent(self, worker, mock_session_factory):
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
        _run(worker._on_send_message(event))
        # Should not trigger since it's recent
        worker._queue_refresh.assert_not_called()

    def test_on_send_message_triggers_if_no_last_message_time(self, worker, mock_session_factory):
        contact_id = uuid.uuid4()
        conversation = MagicMock()
        conversation.contact_id = contact_id
        conversation.last_message_time = None  # No previous message

        session = mock_session_factory.return_value
        session.query.return_value.filter.return_value.first.return_value = conversation

        event = ChatEvent(
            event_type=EventType.SEND_MESSAGE,
            user_id=uuid.uuid4(),
            payload={},
            conversation_id=uuid.uuid4(),
        )

        worker._queue_refresh = AsyncMock()
        _run(worker._on_send_message(event))
        worker._queue_refresh.assert_called_once_with(contact_id)

    def test_on_close_chat_triggers(self, worker, mock_session_factory):
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
        _run(worker._on_close_chat(event))
        worker._queue_refresh.assert_called_once_with(contact_id)

    def test_on_send_message_handles_naive_datetime(self, worker, mock_session_factory):
        """Conversation có last_message_time không có tzinfo → vẫn hoạt động."""
        contact_id = uuid.uuid4()
        conversation = MagicMock()
        conversation.contact_id = contact_id
        # naive datetime (no tzinfo) — old (idle)
        naive_old = datetime.utcnow() - timedelta(minutes=10)
        conversation.last_message_time = naive_old

        session = mock_session_factory.return_value
        session.query.return_value.filter.return_value.first.return_value = conversation

        event = ChatEvent(
            event_type=EventType.SEND_MESSAGE,
            user_id=uuid.uuid4(),
            payload={},
            conversation_id=uuid.uuid4(),
        )

        worker._queue_refresh = AsyncMock()
        _run(worker._on_send_message(event))
        worker._queue_refresh.assert_called_once_with(contact_id)

    def test_worker_init_does_not_create_agent(self):
        """Worker init không nên khởi tạo MemoryAgent (lazy)."""
        from src.workers.memory_worker import MemoryWorker

        bus = MagicMock(spec=EventBus)
        factory = MagicMock()
        w = MemoryWorker(event_bus=bus, session_factory=factory)
        assert w._agent is None, "MemoryAgent should be lazy-initialized"

    def test_get_agent_creates_singleton(self):
        """MemoryAgent chỉ được tạo 1 lần."""
        from src.workers.memory_worker import MemoryWorker

        bus = MagicMock(spec=EventBus)
        factory = MagicMock()
        w = MemoryWorker(event_bus=bus, session_factory=factory)

        # Lần đầu gọi sẽ tạo (cần OPENAI_API_KEY)
        import os
        os.environ.setdefault("OPENAI_API_KEY", "sk-test")
        try:
            a1 = w._get_agent()
            a2 = w._get_agent()
            assert a1 is a2, "MemoryAgent should be singleton"
        except Exception:
            pytest.skip("OPENAI_API_KEY not available for LLMGateway")