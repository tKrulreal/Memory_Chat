import uuid
from fastapi import WebSocket
from src.core.metrics import websocket_active_connections, websocket_disconnects_total


class ConnectionManager:
    def __init__(self):
        self._connections: dict[uuid.UUID, set[WebSocket]] = {}
        self._online_users: set[uuid.UUID] = set()

    async def connect(self, websocket: WebSocket, user_id: uuid.UUID, is_visible: bool = True) -> None:
        await websocket.accept()
        self._connections.setdefault(user_id, set()).add(websocket)
        websocket_active_connections.inc()

        if is_visible:
            was_offline = user_id not in self._online_users
            self._online_users.add(user_id)
            if was_offline:
                # Broadcast new online user to all active clients
                await self.broadcast_all({
                    "type": "USER_PRESENCE",
                    "user_id": str(user_id),
                    "is_online": True,
                })

        # Send current online users list to this connected client
        try:
            await websocket.send_json({
                "type": "ONLINE_USERS",
                "user_ids": [str(uid) for uid in self._online_users if uid != user_id],
            })
        except Exception:
            pass

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
            if user_id in self._online_users:
                self._online_users.discard(user_id)

    async def broadcast_user_offline(self, user_id: uuid.UUID) -> None:
        """Broadcast offline event after websocket disconnection cleanup."""
        if user_id not in self._connections:
            await self.broadcast_all({
                "type": "USER_PRESENCE",
                "user_id": str(user_id),
                "is_online": False,
            })

    async def broadcast_to_user(self, user_id: uuid.UUID, message: dict) -> None:
        for websocket in list(self._connections.get(user_id, set())):
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(websocket, user_id)

    async def broadcast_all(self, message: dict) -> None:
        for user_id, conns in list(self._connections.items()):
            for ws in list(conns):
                try:
                    await ws.send_json(message)
                except Exception:
                    self.disconnect(ws, user_id)

    def is_online(self, user_id: uuid.UUID) -> bool:
        return user_id in self._online_users

    def get_online_user_ids(self) -> list[str]:
        return [str(uid) for uid in self._online_users]
