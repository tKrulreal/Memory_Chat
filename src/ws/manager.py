import uuid

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: dict[uuid.UUID, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: uuid.UUID) -> None:
        await websocket.accept()
        self._connections.setdefault(conversation_id, set()).add(websocket)

    def disconnect(self, websocket: WebSocket, conversation_id: uuid.UUID) -> None:
        connections = self._connections.get(conversation_id)
        if connections is None:
            return
        connections.discard(websocket)
        if not connections:
            del self._connections[conversation_id]

    async def broadcast(self, conversation_id: uuid.UUID, message: dict) -> None:
        for websocket in list(self._connections.get(conversation_id, set())):
            try:
                await websocket.send_json(message)
            except RuntimeError:
                self.disconnect(websocket, conversation_id)
