import uuid
from typing import Annotated, Any
from pydantic import BaseModel



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

    # If tags not yet populated, auto-generate high-signal tags with TaggingAgent
    if "tags" not in context_data or not context_data["tags"]:
        try:
            from src.agents.tagging import TaggingAgent
            agent = TaggingAgent()
            generated_tags = agent.generate_tags(conversation_id, current_user.id, db)
            context_data["tags"] = generated_tags
        except Exception as e:
            logging.getLogger(__name__).warning("Auto tagging failed: %s", e)
            context_data["tags"] = []

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
    
    # Sync with Qdrant
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
        logging.getLogger(__name__).warning("Failed to sync updated context to Qdrant: %s", e)
        
    context_data = memory.facts or {}
    context_data["summary"] = memory.summary
    return AIContext.model_validate(context_data)


@router.post("/{conversation_id}/assistant/context/refresh", response_model=AIContext)
async def trigger_context_refresh(
    conversation_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ConversationServiceDep,
    event_bus: EventBusDep,
):
    """
    Kích hoạt AI truy xuất toàn bộ tin nhắn từ DB, phân tích và tóm tắt lại ngữ cảnh đối phương.
    """
    _get_owned_conversation(service, db, current_user.id, conversation_id)

    from src.models.chat import Message
    from src.agents.memory.agent import MemoryAgent

    # 1. Lấy toàn bộ tin nhắn trong cuộc trò chuyện
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    msg_dicts = [
        {
            "content": m.content,
            "sender_user_id": str(m.sender_user_id),
            "created_at": m.created_at,
        }
        for m in messages
    ]

    # 2. Chạy MemoryAgent để tóm tắt và trích xuất thực thể
    memory_agent = MemoryAgent()
    try:
        memory_res = await memory_agent.build_memory(
            user_id=current_user.id,
            conversation_id=conversation_id,
            messages=msg_dicts,
        )
    except Exception as e:
        logging.getLogger(__name__).error("Failed to build memory: %s", e)
        memory_res = None

    # 3. Cập nhật AssistantMemory trong database
    memory = (
        db.query(AssistantMemory)
        .filter(
            AssistantMemory.owner_user_id == current_user.id,
            AssistantMemory.conversation_id == conversation_id,
        )
        .first()
    )

    if not memory:
        memory = AssistantMemory(
            owner_user_id=current_user.id,
            conversation_id=conversation_id,
            facts={},
            summary="",
        )
        db.add(memory)

    facts = dict(memory.facts or {})
    if memory_res:
        memory.summary = memory_res.summary
        facts["last_met"] = memory_res.last_met
        facts["interested_in"] = memory_res.interested_in
        facts["follow_up"] = memory_res.follow_up
        facts["relationship_score"] = memory_res.relationship_score
        facts["timeline"] = memory_res.timeline
    
    memory.facts = facts
    db.commit()
    db.refresh(memory)

    # 4. Đồng bộ với Qdrant vector store
    try:
        facts_str = "\n".join([f"- {k}: {v}" for k, v in facts.items()])
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
        logging.getLogger(__name__).warning("Failed to sync updated context to Qdrant: %s", e)

    # 5. Phát sự kiện thông báo cập nhật
    event_bus.publish(
        db=db,
        event_type=EventType.MEMORY_UPDATED,
        user_id=current_user.id,
        payload={},
        conversation_id=conversation_id,
    )
    db.commit()

    context_data = dict(memory.facts or {})
    context_data["summary"] = memory.summary
    return AIContext.model_validate(context_data)


@router.get("/{conversation_id}/assistant/suggested-reply")
def get_suggested_reply(
    conversation_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ConversationServiceDep,
) -> dict[str, Any]:
    """
    Lấy câu trả lời gợi ý (Smart Reply) cho tin nhắn gần nhất mà đối phương đã nhắn.
    """
    _get_owned_conversation(service, db, current_user.id, conversation_id)

    from src.agents.reply import ReplySuggestionAgent
    agent = ReplySuggestionAgent()
    return agent.generate_suggested_reply(conversation_id, current_user.id, db)


@router.post("/{conversation_id}/assistant/suggested-reply/refresh")
def refresh_suggested_reply(
    conversation_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ConversationServiceDep,
) -> dict[str, Any]:
    """
    Yêu cầu AI sinh lại câu trả lời gợi ý mới nhất cho tin nhắn gần đây của đối phương.
    """
    _get_owned_conversation(service, db, current_user.id, conversation_id)

    from src.agents.reply import ReplySuggestionAgent
    agent = ReplySuggestionAgent()
    return agent.generate_suggested_reply(conversation_id, current_user.id, db)



class TagUpdateRequest(BaseModel):
    tags: list[str]


@router.post("/{conversation_id}/assistant/tags/refresh")
def refresh_assistant_tags(
    conversation_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ConversationServiceDep,
) -> dict[str, Any]:
    """
    Kích hoạt Agent phân tích lại toàn bộ đoạn chat và tự động gắn các tag quan trọng cho đối phương.
    """
    _get_owned_conversation(service, db, current_user.id, conversation_id)

    from src.agents.tagging import TaggingAgent
    agent = TaggingAgent()
    tags = agent.generate_tags(conversation_id, current_user.id, db)
    return {"tags": tags}


@router.put("/{conversation_id}/assistant/tags")
def update_assistant_tags(
    conversation_id: uuid.UUID,
    payload: TagUpdateRequest,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ConversationServiceDep,
) -> dict[str, Any]:
    """
    Người dùng điều chỉnh (thêm/xóa) danh sách tag của đối phương.
    """
    _get_owned_conversation(service, db, current_user.id, conversation_id)

    from src.agents.tagging.agent import TaggingAgent
    agent = TaggingAgent()
    cleaned_tags = agent._clean_tags(payload.tags)

    memory = (
        db.query(AssistantMemory)
        .filter(
            AssistantMemory.owner_user_id == current_user.id,
            AssistantMemory.conversation_id == conversation_id,
        )
        .first()
    )

    if not memory:
        memory = AssistantMemory(
            owner_user_id=current_user.id,
            conversation_id=conversation_id,
            facts={"tags": cleaned_tags},
            summary="",
        )
        db.add(memory)
    else:
        facts = dict(memory.facts or {})
        facts["tags"] = cleaned_tags
        memory.facts = facts

    db.commit()
    db.refresh(memory)
    return {"tags": cleaned_tags}

