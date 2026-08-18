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
    
    import time
    last_activity = time.time()
    
    async def receive_loop():
        nonlocal last_activity
        while True:
            payload = await websocket.receive_json()
            last_activity = time.time()
            # WS is now one-way for chat messages.
            # Client must use POST /messages to send.
            if payload.get("type") == "pong":
                continue
            # We can support typing indicators here later.

    async def ping_loop():
        while True:
            await asyncio.sleep(30)
            if time.time() - last_activity > 65:
                # Client missed two pings, disconnect
                await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
                break
            try:
                await websocket.send_json({"type": "ping"})
            except Exception:
                break

    receiver_task = asyncio.create_task(receive_loop())
    pinger_task = asyncio.create_task(ping_loop())

    try:
        # Wait until either task fails/completes
        done, pending = await asyncio.wait(
            [receiver_task, pinger_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, user.id)
