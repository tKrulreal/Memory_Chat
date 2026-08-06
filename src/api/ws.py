import asyncio
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_websocket_event_bus
from src.core.security import get_user_from_token
from src.events.bus import EventBus
from src.events.types import EventType
from src.repositories.conversation import ConversationRepository
from src.repositories.message import MessageRepository
from src.schemas.enums import MessageRole
from src.schemas.message import MessageCreate, MessageResponse
from src.services.message import MessageConversationNotFoundError, MessageOwnershipError, MessageService
from src.ws.manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()

DatabaseDep = Annotated[Session, Depends(get_db)]
EventBusDep = Annotated[EventBus, Depends(get_websocket_event_bus)]


def get_message_service() -> MessageService:
    return MessageService(MessageRepository(), ConversationRepository())


@router.websocket("/ws/chat/{conversation_id}")
async def chat_websocket(
    websocket: WebSocket,
    conversation_id: uuid.UUID,
    token: Annotated[str, Query()],
    db: DatabaseDep,
    event_bus: EventBusDep,
    service: Annotated[MessageService, Depends(get_message_service)],
):
    user = get_user_from_token(token, db)
    if user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        service.list_messages(db, user.id, conversation_id, page=1, limit=1)
    except (MessageConversationNotFoundError, MessageOwnershipError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, conversation_id)
    try:
        while True:
            try:
                payload = await asyncio.wait_for(websocket.receive_json(), timeout=30)
            except TimeoutError:
                await websocket.send_json({"type": "ping"})
                continue
            if payload.get("type") == "pong":
                continue
            try:
                message_in = MessageCreate(content=payload["content"], role=MessageRole.USER)
                message = service.create_message(db, user.id, conversation_id, message_in)
            except (KeyError, ValueError):
                await websocket.send_json({"type": "error", "detail": "Invalid message payload"})
                continue
            await event_bus.publish(
                EventType.SEND_MESSAGE,
                user.id,
                {"message_id": str(message.id), "role": message.sender_type, "content": message.content},
                conversation_id,
            )
            await manager.broadcast(conversation_id, MessageResponse.model_validate(message).model_dump(mode="json"))
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, conversation_id)
