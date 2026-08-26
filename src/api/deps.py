from collections.abc import Generator

from fastapi import Request, WebSocket

from src.events.bus import EventBus
from src.models.database import SessionLocal


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_event_bus(request: Request) -> EventBus:
    return request.app.state.event_bus


def get_websocket_event_bus(websocket: WebSocket) -> EventBus:
    return websocket.app.state.event_bus
