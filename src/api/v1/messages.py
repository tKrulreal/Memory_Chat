import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_event_bus
from src.core.security import get_current_user
from src.events.bus import EventBus
from src.events.types import EventType
from src.models.user import User
from src.repositories.conversation import ConversationRepository
from src.repositories.message import MessageRepository
from src.schemas.message import MessageCreate, MessageResponse
from src.schemas.pagination import PaginatedResponse, Pagination
from src.services.message import (
    MessageConflictError,
    MessageConversationNotFoundError,
    MessageNotFoundError,
    MessageOwnershipError,
    MessageService,
)

router = APIRouter()


def get_message_service() -> MessageService:
    return MessageService(MessageRepository(), ConversationRepository())


MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
DatabaseDep = Annotated[Session, Depends(get_db)]
EventBusDep = Annotated[EventBus, Depends(get_event_bus)]


@router.get("/direct-conversations/{conversation_id}/messages", response_model=PaginatedResponse[MessageResponse])
def list_messages(
    conversation_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: MessageServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=50)] = 50,
):
    try:
        messages, total = service.list_messages(db, current_user.id, conversation_id, page, limit)
    except MessageConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found") from None
    except MessageOwnershipError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this conversation") from None
    return PaginatedResponse(
        data=[MessageResponse.model_validate(message) for message in messages],
        pagination=Pagination(page=page, limit=limit, total=total),
    )


@router.post("/direct-conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    conversation_id: uuid.UUID,
    message_in: MessageCreate,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: MessageServiceDep,
    event_bus: EventBusDep,
):
    try:
        message = service.create_message(db, current_user.id, conversation_id, message_in, event_bus)
    except MessageConflictError as e:
        # Idempotency: Return 409 as requested by user
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Message already exists") from None
    except MessageConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found") from None
    except MessageOwnershipError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this conversation") from None
        
    # Fan-out to connected websocket clients
    from src.api.ws import manager
    conversation = service.conversation_repository.get(db, id=conversation_id)
    msg_dict = MessageResponse.model_validate(message).model_dump(mode="json")
    msg_dict["type"] = "NEW_MESSAGE"
    if conversation:
        await manager.broadcast_to_user(conversation.user_a_id, msg_dict)
        await manager.broadcast_to_user(conversation.user_b_id, msg_dict)

    return MessageResponse.model_validate(message)


@router.get("/messages/{message_id}", response_model=MessageResponse)
def get_message(
    message_id: uuid.UUID, current_user: CurrentUserDep, db: DatabaseDep, service: MessageServiceDep
):
    return MessageResponse.model_validate(_get_owned_message(service, db, current_user.id, message_id))


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: uuid.UUID, current_user: CurrentUserDep, db: DatabaseDep, service: MessageServiceDep
) -> Response:
    message = service.delete_message(db, current_user.id, message_id)
    
    # Broadcast MESSAGE_RECALLED event
    from src.api.ws import manager
    conversation = service.conversation_repository.get(db, id=message.conversation_id)
    if conversation:
        event_payload = {
            "type": "MESSAGE_RECALLED",
            "conversation_id": str(message.conversation_id),
            "message_id": str(message.id),
            "deleted_at": message.deleted_at.isoformat() if message.deleted_at else None,
        }
        await manager.broadcast_to_user(conversation.user_a_id, event_payload)
        await manager.broadcast_to_user(conversation.user_b_id, event_payload)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _get_owned_message(service: MessageService, db: Session, user_id: uuid.UUID, message_id: uuid.UUID):
    try:
        return service.get_owned_message(db, user_id, message_id)
    except MessageNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found") from None
    except MessageConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found") from None
    except MessageOwnershipError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this message") from None
