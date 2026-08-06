import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_event_bus
from src.core.security import get_current_user
from src.events.bus import EventBus
from src.events.types import EventType
from src.models.user import User
from src.repositories.contact import ContactRepository
from src.repositories.conversation import ConversationRepository
from src.schemas.conversation import ConversationCreate, ConversationResponse, ConversationUpdate
from src.schemas.enums import ConversationStatus
from src.schemas.pagination import PaginatedResponse, Pagination
from src.services.conversation import (
    ConversationContactError,
    ConversationNotFoundError,
    ConversationOwnershipError,
    ConversationService,
)

router = APIRouter()


def get_conversation_service() -> ConversationService:
    return ConversationService(ConversationRepository(), ContactRepository())


ConversationServiceDep = Annotated[ConversationService, Depends(get_conversation_service)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
DatabaseDep = Annotated[Session, Depends(get_db)]
EventBusDep = Annotated[EventBus, Depends(get_event_bus)]


@router.get("", response_model=PaginatedResponse[ConversationResponse])
def list_conversations(
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ConversationServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    status_filter: ConversationStatus | None = Query(default=None, alias="status"),
    contact_id: uuid.UUID | None = None,
):
    try:
        conversations, total = service.list_conversations(
            db, current_user.id, page, limit, status_filter, contact_id
        )
    except ConversationContactError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this contact") from None
    return PaginatedResponse(
        data=[ConversationResponse.model_validate(conversation) for conversation in conversations],
        pagination=Pagination(page=page, limit=limit, total=total),
    )


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_in: ConversationCreate,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ConversationServiceDep,
    event_bus: EventBusDep,
):
    try:
        conversation = service.create_conversation(db, current_user.id, conversation_in)
    except ConversationContactError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this contact") from None
    await event_bus.publish(
        EventType.OPEN_CHAT,
        current_user.id,
        {"conversation_id": str(conversation.id)},
        conversation.id,
    )
    return ConversationResponse.model_validate(conversation)


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ConversationServiceDep,
):
    return ConversationResponse.model_validate(_get_owned_conversation(service, db, current_user.id, conversation_id))


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: uuid.UUID,
    conversation_in: ConversationUpdate,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ConversationServiceDep,
    event_bus: EventBusDep,
):
    try:
        conversation, closed_now = service.update_conversation(db, current_user.id, conversation_id, conversation_in)
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found") from None
    except ConversationOwnershipError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this conversation") from None
    if closed_now:
        await event_bus.publish(
            EventType.CLOSE_CHAT,
            current_user.id,
            {"conversation_id": str(conversation.id)},
            conversation.id,
        )
    return ConversationResponse.model_validate(conversation)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ConversationServiceDep,
) -> Response:
    try:
        service.delete_conversation(db, current_user.id, conversation_id)
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found") from None
    except ConversationOwnershipError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this conversation") from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _get_owned_conversation(
    service: ConversationService,
    db: Session,
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
):
    try:
        return service.get_owned_conversation(db, user_id, conversation_id)
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found") from None
    except ConversationOwnershipError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this conversation") from None
