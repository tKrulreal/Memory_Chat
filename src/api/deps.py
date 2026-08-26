from collections.abc import Generator

from fastapi import Request, WebSocket

from src.events.bus import EventBus
from src.models.database import SessionLocal


_default_event_bus: EventBus | None = None


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_event_bus(request: Request) -> EventBus:
    global _default_event_bus
    if hasattr(request.app, "state") and hasattr(request.app.state, "event_bus") and request.app.state.event_bus is not None:
        return request.app.state.event_bus
    if _default_event_bus is None:
        _default_event_bus = EventBus()
    return _default_event_bus


def get_websocket_event_bus(websocket: WebSocket) -> EventBus:
    global _default_event_bus
    if hasattr(websocket.app, "state") and hasattr(websocket.app.state, "event_bus") and websocket.app.state.event_bus is not None:
        return websocket.app.state.event_bus
    if _default_event_bus is None:
        _default_event_bus = EventBus()
    return _default_event_bus
