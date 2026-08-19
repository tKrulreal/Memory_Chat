import uuid

from fastapi import WebSocket
from src.core.metrics import websocket_active_connections, websocket_disconnects_total

class ConnectionManager:
    def __init__(self):
        self._connections: dict[uuid.UUID, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: uuid.UUID) -> None:
        await websocket.accept()
        self._connections.setdefault(user_id, set()).add(websocket)
        websocket_active_connections.inc()

    def disconnect(self, websocket: WebSocket, user_id: uuid.UUID) -> None:
        connections = self._connections.get(user_id)
        if connections is None:
            return
        if websocket in connections:
            connections.discard(websocket)
            websocket_active_connections.dec()
            websocket_disconnects_total.inc()
        if not connections:
            del self._connections[user_id]

    async def broadcast_to_user(self, user_id: uuid.UUID, message: dict) -> None:
        for websocket in list(self._connections.get(user_id, set())):
            try:
                await websocket.send_json(message)
            except RuntimeError:
                self.disconnect(websocket, user_id)
