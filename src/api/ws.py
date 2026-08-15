import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_websocket_event_bus
from src.core.security import get_user_from_ws_ticket
from src.events.bus import EventBus
from src.ws.manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()

DatabaseDep = Annotated[Session, Depends(get_db)]
EventBusDep = Annotated[EventBus, Depends(get_websocket_event_bus)]


@router.websocket("/ws/chat")
async def chat_websocket(
    websocket: WebSocket,
    ticket: Annotated[str, Query()],
    db: DatabaseDep,
    event_bus: EventBusDep,
):
    user = get_user_from_ws_ticket(ticket, db)
    if user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, user.id)
    try:
        while True:
            try:
                payload = await asyncio.wait_for(websocket.receive_json(), timeout=30)
            except TimeoutError:
                await websocket.send_json({"type": "ping"})
                continue
            if payload.get("type") == "pong":
                continue
            # WS is now one-way. Client must use POST /messages to send.
            # We can support typing indicators here later.
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, user.id)
