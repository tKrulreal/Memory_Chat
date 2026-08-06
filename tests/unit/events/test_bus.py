import pytest
from sqlalchemy.orm import Session, sessionmaker

from src.events.bus import EventBus
from src.events.types import EventType
from src.models.ai import EventLog


@pytest.mark.asyncio
async def test_event_bus_persists_and_dispatches(db_session: Session, current_user):
    received = []
    bus = EventBus(sessionmaker(bind=db_session.get_bind()))

    async def handler(event):
        received.append(event)

    bus.subscribe(EventType.SEND_MESSAGE, handler)
    await bus.start()
    await bus.publish(EventType.SEND_MESSAGE, current_user.id, {"content": "Hello"})
    await bus.join()

    db_session.expire_all()
    event_log = db_session.query(EventLog).one()
    assert event_log.event_type == EventType.SEND_MESSAGE
    assert event_log.user_id == current_user.id
    assert event_log.payload == {"content": "Hello"}
    assert received[0].payload == {"content": "Hello"}

    await bus.stop()


@pytest.mark.asyncio
async def test_event_bus_keeps_dispatching_when_a_handler_fails(db_session: Session, current_user):
    received = []
    bus = EventBus(sessionmaker(bind=db_session.get_bind()))

    def failing_handler(_event):
        raise RuntimeError("expected failure")

    def working_handler(event):
        received.append(event.event_type)

    bus.subscribe(EventType.OPEN_CHAT, failing_handler)
    bus.subscribe(EventType.OPEN_CHAT, working_handler)
    await bus.start()
    await bus.publish(EventType.OPEN_CHAT, current_user.id, {})
    await bus.join()

    assert received == [EventType.OPEN_CHAT]
    assert db_session.query(EventLog).count() == 1

    await bus.stop()
