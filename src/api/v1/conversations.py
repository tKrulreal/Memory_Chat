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
from src.schemas.ai import AIContext
from src.schemas.conversation import ConversationCreate, ConversationResponse, ConversationUpdate
from src.schemas.enums import ConversationStatus
from src.schemas.pagination import PaginatedResponse, Pagination
from src.services.conversation import (
    ConversationDuplicateError,
    ConversationNotFoundError,
    ConversationOwnershipError,
    ConversationService,
)
from src.models.ai import AssistantMemory
from src.services.vector_store import VectorStoreService
from src.gateways.llm import LLMGateway

router = APIRouter()


def get_conversation_service() -> ConversationService:
    return ConversationService(ConversationRepository())


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
):
    conversations, total = service.list_conversations(
        db, current_user.id, page, limit, status_filter
    )
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
    if not conversation_in.target_user_id and conversation_in.peer_email:
        from src.models.user import User
        peer = db.query(User).filter(User.email == conversation_in.peer_email).first()
        if not peer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        conversation_in.target_user_id = peer.id

    if not conversation_in.target_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide target_user_id or peer_email")

    try:
        conversation = service.create_conversation(db, current_user.id, conversation_in, event_bus)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
    
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
        conversation, closed_now = service.update_conversation(db, current_user.id, conversation_id, conversation_in, event_bus)
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found") from None
    except ConversationOwnershipError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this conversation") from None
    
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


@router.get("/{conversation_id}/assistant/context", response_model=AIContext)
def get_assistant_context(
    conversation_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ConversationServiceDep,
):
    # Verify ownership
    _get_owned_conversation(service, db, current_user.id, conversation_id)

    memory = db.query(AssistantMemory).filter(
        AssistantMemory.owner_user_id == current_user.id,
        AssistantMemory.conversation_id == conversation_id
    ).first()

    if not memory:
        # Auto-create empty context if it doesn't exist yet
        memory = AssistantMemory(
            owner_user_id=current_user.id,
            conversation_id=conversation_id,
            facts={},
            summary="",
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)

    context_data = memory.facts or {}
    context_data["summary"] = memory.summary
    return AIContext.model_validate(context_data)


@router.patch("/{conversation_id}/assistant/context", response_model=AIContext)
def update_assistant_context(
    conversation_id: uuid.UUID,
    context_in: AIContext,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ConversationServiceDep,
    event_bus: EventBusDep,
):
    # Verify ownership
    _get_owned_conversation(service, db, current_user.id, conversation_id)
    
    memory = db.query(AssistantMemory).filter(
        AssistantMemory.owner_user_id == current_user.id,
        AssistantMemory.conversation_id == conversation_id
    ).with_for_update().first()
    
    if not memory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Context not found")
        
    # Update facts and summary
    old_facts = memory.facts or {}
    new_data = context_in.model_dump()
    new_summary = new_data.pop("summary", None)
    
    old_facts.update(new_data)
    memory.facts = old_facts
    if new_summary is not None:
        memory.summary = new_summary
    
    db.commit()
    db.refresh(memory)
    
    # Notify clients
    event_bus.publish(
        db=db,
        event_type=EventType.MEMORY_UPDATED,
        user_id=current_user.id,
        payload={},
        conversation_id=conversation_id,
    )
    db.commit()
    
    # Sync with ChromaDB
    try:
        facts_str = "\n".join([f"- {k}: {v}" for k, v in (memory.facts or {}).items()])
        text_for_embedding = f"Summary: {memory.summary}\nFacts:\n{facts_str}"
        
        llm = LLMGateway()
        embedding = llm.embed(text_for_embedding)
        
        vector_store = VectorStoreService.get_instance()
        vector_store.upsert(
            memory_id=str(memory.id),
            text=text_for_embedding,
            embedding=embedding,
            metadata={
                "owner_user_id": str(current_user.id),
                "conversation_id": str(conversation_id),
                "updated_at": memory.updated_at.isoformat() if memory.updated_at else None,
            },
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Failed to sync updated context to ChromaDB: %s", e)
        
    context_data = memory.facts or {}
    context_data["summary"] = memory.summary
    return AIContext.model_validate(context_data)


@router.post("/{conversation_id}/assistant/context/refresh", status_code=status.HTTP_202_ACCEPTED)
def trigger_context_refresh(
    conversation_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ConversationServiceDep,
    event_bus: EventBusDep,
):
    # Verify ownership
    _get_owned_conversation(service, db, current_user.id, conversation_id)
    
    event_bus.publish(
        db=db,
        event_type=EventType.OPEN_AI,
        user_id=current_user.id,
        payload={},
        conversation_id=conversation_id,
    )
    db.commit()
    return {"status": "accepted"}
