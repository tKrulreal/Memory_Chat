"""
AI Copilot API — TASK-COP-05.

Endpoints:
- POST /chat              — Hỏi Copilot (gọi Assistant Orchestrator)
- POST /stream            — Streaming response (optional)
- POST /share             — Share AI response vào conversation input box
"""

import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.core.security import get_current_user
from src.models.chat import Conversation, Message
from src.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

CurrentUserDep = Annotated[User, Depends(get_current_user)]
DatabaseDep = Annotated[Session, Depends(get_db)]


# =============================================================================
# Schemas
# =============================================================================

class CopilotContext(BaseModel):
    """Context cho copilot request."""
    contact_id: str | None = None
    conversation_id: str | None = None

    model_config = {"extra": "forbid"}


class CopilotRequest(BaseModel):
    """Request body cho copilot."""
    query: str = Field(..., min_length=1, max_length=1000, description="Câu hỏi của user")
    context: CopilotContext | None = None

    model_config = {"extra": "forbid"}


class CopilotToolUsed(BaseModel):
    """Tool đã được sử dụng."""
    tool: str
    success: bool


class CopilotMessageItem(BaseModel):
    """Item tin nhắn trong lịch sử Copilot."""
    id: uuid.UUID
    role: str
    content: str
    tools_used: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    intent: str | None = None
    conversation_id: uuid.UUID | None = None
    created_at: str

    model_config = {"from_attributes": True}


class CopilotResponse(BaseModel):
    """Response từ copilot."""
    id: uuid.UUID | None = None
    response: str = Field(..., description="Câu trả lời của AI")
    intent: str = Field(..., description="Intent đã được detect")
    tools_used: list[str] = Field(default_factory=list, description="Tools đã sử dụng")
    sources: list[str] = Field(default_factory=list, description="Nguồn dữ liệu đã sử dụng")
    is_valid: bool = Field(default=True, description="Response có valid không")

    model_config = {"from_attributes": True}


class ShareRequest(BaseModel):
    """Request để share AI response vào conversation."""
    conversation_id: str = Field(..., description="UUID của conversation")
    content: str = Field(..., min_length=1, max_length=5000, description="Nội dung AI response để share")
    save_to_draft: bool = Field(
        default=False,
        description="True = lưu vào draft, False = tạo message thật (default: tạo draft)"
    )

    model_config = {"extra": "forbid"}


class ShareResponse(BaseModel):
    """Response sau khi share."""
    status: str
    message: str
    conversation_id: str
    content: str


# =============================================================================
# Helpers
# =============================================================================

def _verify_conversation_access(
    db: Session,
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
) -> Conversation:
    """Verify user owns the conversation."""
    from src.models.chat import Conversation
    conv = db.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    if conv.user_a_id != user_id and conv.user_b_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this conversation",
        )
    return conv


def _log_copilot_interaction(
    user_id: uuid.UUID,
    query: str,
    response: str,
    intent: str,
    tools_used: list[str],
) -> None:
    """Log copilot interaction vào file."""
    import json
    import os
    from datetime import datetime

    log_dir = ".ai-log"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "copilot.jsonl")

    entry = {
        "ts": datetime.now().isoformat(),
        "user_id": str(user_id),
        "query": query,
        "response": response,
        "intent": intent,
        "tools_used": tools_used,
    }

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning(f"Failed to log copilot interaction: {e}")


def _emit_open_ai_event(
    request,
    user_id: uuid.UUID,
    conversation_id: uuid.UUID | None,
    contact_id: uuid.UUID | None,
) -> None:
    """Emit OPEN_AI event để trigger background processing."""
    from src.events.types import EventType

    payload = {"query_type": "copilot"}
    if conversation_id:
        payload["conversation_id"] = str(conversation_id)
    if contact_id:
        payload["contact_id"] = str(contact_id)

    if request is not None and hasattr(request, "app") and hasattr(request.app.state, "event_bus"):
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(
                    request.app.state.event_bus.publish(
                        EventType.OPEN_AI,
                        user_id=user_id,
                        payload=payload,
                        conversation_id=conversation_id,
                    )
                )
        except Exception:
            pass  # Best effort


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/messages", response_model=list[CopilotMessageItem])
def get_copilot_messages(
    current_user: CurrentUserDep,
    db: DatabaseDep,
    limit: int = 100,
    conversation_id: uuid.UUID | None = None,
) -> list[CopilotMessageItem]:
    """
    Lấy danh sách tin nhắn đã chat với Copilot của user hiện tại.
    - Nếu conversation_id được cung cấp: Trả về tin nhắn Copilot riêng cho cuộc hội thoại đó.
    - Nếu conversation_id là None: Trả về tin nhắn Copilot toàn cục (Global Copilot).
    """
    from src.models.ai import CopilotMessage

    query = db.query(CopilotMessage).filter(CopilotMessage.user_id == current_user.id)
    if conversation_id:
        _verify_conversation_access(db, current_user.id, conversation_id)
        query = query.filter(CopilotMessage.conversation_id == conversation_id)
    else:
        query = query.filter(CopilotMessage.conversation_id.is_(None))

    messages = (
        query
        .order_by(CopilotMessage.created_at.asc())
        .limit(limit)
        .all()
    )

    return [
        CopilotMessageItem(
            id=m.id,
            role=m.role,
            content=m.content,
            tools_used=m.tools_used or [],
            sources=m.sources or [],
            intent=m.intent,
            conversation_id=m.conversation_id,
            created_at=m.created_at.isoformat() if m.created_at else "",
        )
        for m in messages
    ]


@router.delete("/messages")
def clear_copilot_messages(
    current_user: CurrentUserDep,
    db: DatabaseDep,
    conversation_id: uuid.UUID | None = None,
) -> dict[str, Any]:
    """
    Xóa lịch sử tin nhắn Copilot của user hiện tại (riêng cho conversation_id hoặc toàn cục).
    """
    from src.models.ai import CopilotMessage

    query = db.query(CopilotMessage).filter(CopilotMessage.user_id == current_user.id)
    if conversation_id:
        _verify_conversation_access(db, current_user.id, conversation_id)
        query = query.filter(CopilotMessage.conversation_id == conversation_id)
    else:
        query = query.filter(CopilotMessage.conversation_id.is_(None))

    deleted = query.delete(synchronize_session=False)
    db.commit()
    return {"status": "success", "deleted_count": deleted}


@router.post("", response_model=CopilotResponse)
async def copilot_chat(
    payload: CopilotRequest,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    request: Any = None,  # FastAPI Request
) -> CopilotResponse:
    """
    Hỏi AI Copilot.
    Tách biệt ngữ cảnh hoàn toàn:
    - Nếu payload.context.conversation_id được cung cấp: In-Chat Copilot chỉ phân tích hội thoại cụ thể.
    - Nếu không có conversation_id: Global AI Copilot hỗ trợ tìm kiếm toàn hệ thống.
    """
    import re
    from datetime import datetime, timedelta, timezone
    from src.models.ai import CopilotMessage
    from src.models.user import Setting
    from src.models.tag import AISystemConfig
    from src.agents import run_copilot
    from src.core.guardrails import (
        validate_input_query,
        verify_in_chat_access,
        sanitize_output_response,
        GuardrailException,
    )

    try:
        clean_query = validate_input_query(payload.query)
    except GuardrailException as ge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ge.message,
        )

    conv_id_obj: uuid.UUID | None = None
    if payload.context and payload.context.conversation_id:
        try:
            verify_in_chat_access(db, current_user.id, payload.context.conversation_id)
            conv_id_obj = uuid.UUID(payload.context.conversation_id)
        except GuardrailException as ge:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN if ge.code == "UNAUTHORIZED_ACCESS" else status.HTTP_400_BAD_REQUEST,
                detail=ge.message,
            )

    # 1. Lưu tin nhắn người dùng gửi vào database với conversation_id tương ứng
    user_msg_db = CopilotMessage(
        id=uuid.uuid4(),
        user_id=current_user.id,
        conversation_id=conv_id_obj,
        role="user",
        content=clean_query,
    )
    db.add(user_msg_db)
    db.commit()
    db.refresh(user_msg_db)

    try:
        # 2. Đọc cài đặt AI Hub (ai_settings & setting)
        ai_config = db.query(AISystemConfig).filter(
            AISystemConfig.user_id == current_user.id,
            AISystemConfig.key == "ai_settings"
        ).first()

        features = {}
        if ai_config and isinstance(ai_config.value, dict):
            features = ai_config.value.get("features", {})
            
        # Kiểm tra toggle tính năng
        if conv_id_obj:
            if features.get("chat_copilot") is False or features.get("copilot") is False:
                raise HTTPException(status_code=400, detail="Tính năng In-Chat Copilot đã bị tắt trong AI Hub.")
        else:
            if features.get("copilot") is False:
                raise HTTPException(status_code=400, detail="Tính năng AI Copilot đã bị tắt trong AI Hub.")

        setting = db.query(Setting).filter(Setting.user_id == current_user.id).first()
        context_turns = 10
        if setting and setting.ai_copilot_context_turns:
            context_turns = setting.ai_copilot_context_turns

        memory_window_days = None
        if setting and setting.ai_memory_window and str(setting.ai_memory_window).lower() != "unlimited":
            try:
                match = re.search(r'\d+', str(setting.ai_memory_window))
                if match:
                    memory_window_days = int(match.group())
            except Exception:
                pass

        # Lấy lịch sử hội thoại Copilot tương ứng (cùng conversation_id hoặc cùng None)
        hist_query = db.query(CopilotMessage).filter(
            CopilotMessage.user_id == current_user.id,
            CopilotMessage.id != user_msg_db.id,
        )
        if conv_id_obj:
            hist_query = hist_query.filter(CopilotMessage.conversation_id == conv_id_obj)
        else:
            hist_query = hist_query.filter(CopilotMessage.conversation_id.is_(None))

        if memory_window_days:
            cutoff = datetime.now(timezone.utc) - timedelta(days=memory_window_days)
            hist_query = hist_query.filter(CopilotMessage.created_at >= cutoff)

        past_msgs = hist_query.order_by(CopilotMessage.created_at.desc()).limit(context_turns * 2).all()
        past_msgs.reverse()

        history_payload = [
            {"role": m.role, "content": m.content}
            for m in past_msgs
        ]

        # Build context
        context_kwargs = {
            "user_id": str(current_user.id),
            "history": history_payload,
        }
        if payload.context:
            if payload.context.contact_id:
                context_kwargs["contact_id"] = payload.context.contact_id
            if payload.context.conversation_id:
                context_kwargs["conversation_id"] = payload.context.conversation_id

        # Run orchestrator
        result = await run_copilot(
            query=payload.query,
            **context_kwargs,
        )

        response_content = result.get("response", "")
        intent_val = result.get("intent", "UNKNOWN")
        tools_used = result.get("tools_used", [])
        sources = result.get("sources", [])

        # 3. Lưu phản hồi của AI vào database
        ai_msg_db = CopilotMessage(
            id=uuid.uuid4(),
            user_id=current_user.id,
            conversation_id=conv_id_obj,
            role="assistant",
            content=response_content,
            tools_used=tools_used,
            sources=sources,
            intent=intent_val,
        )
        db.add(ai_msg_db)
        db.commit()

        # Log interaction
        _log_copilot_interaction(
            user_id=current_user.id,
            query=payload.query,
            response=response_content,
            intent=intent_val,
            tools_used=tools_used,
        )

        # Emit event for background processing
        contact_id = payload.context.contact_id if payload.context else None
        _emit_open_ai_event(
            request,
            current_user.id,
            conv_id_obj,
            uuid.UUID(contact_id) if contact_id else None,
        )

        return CopilotResponse(
            id=ai_msg_db.id,
            response=response_content,
            intent=intent_val,
            tools_used=tools_used,
            sources=sources,
            is_valid=result.get("is_valid", True),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Copilot chat failed: {e}")
        err_msg = "Xin lỗi, hệ thống đang bận. Vui lòng thử lại sau."
        ai_msg_db = CopilotMessage(
            id=uuid.uuid4(),
            user_id=current_user.id,
            conversation_id=conv_id_obj,
            role="assistant",
            content=err_msg,
            tools_used=[],
            intent="ERROR",
        )
        db.add(ai_msg_db)
        db.commit()

        return CopilotResponse(
            id=ai_msg_db.id,
            response=err_msg,
            intent="ERROR",
            tools_used=[],
            is_valid=False,
        )


@router.post("/stream", response_model=CopilotResponse)
async def copilot_chat_stream(
    payload: CopilotRequest,
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> StreamingResponse:
    """
    AI Copilot với streaming response.

    Response được stream về client để hiển thị typing effect.
    """
    from src.agents import run_copilot

    async def generate():
        try:
            conv_id_str = payload.context.conversation_id if payload.context else None
            if conv_id_str:
                _verify_conversation_access(db, current_user.id, uuid.UUID(conv_id_str))

            # Run orchestrator
            result = await run_copilot(
                query=payload.query,
                user_id=str(current_user.id),
                contact_id=payload.context.contact_id if payload.context else None,
                conversation_id=conv_id_str,
            )

            response_text = result.get("response", "")

            # Stream word by word
            for word in response_text.split():
                yield f"data: {word} \n\n"
                import asyncio
                await asyncio.sleep(0.02)  # Small delay for effect

            # Send final event
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Copilot stream failed: {e}")
            yield "data: Xin lỗi, đã xảy ra lỗi.\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post("/share", response_model=ShareResponse)
async def share_to_conversation(
    payload: ShareRequest,
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> ShareResponse:
    """
    Share AI response vào conversation input box.

    Tạo một draft message (USER message type) trong conversation
    để user có thể edit trước khi gửi.

    User phải verify ownership của conversation.
    """
    try:
        conv_id = uuid.UUID(payload.conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation_id format",
        )

    # Verify conversation access
    _verify_conversation_access(db, current_user.id, conv_id)

    # Create draft message
    draft_message = Message(
        conversation_id=conv_id,
        sender_type="USER",
        content=payload.content,
        message_type="DRAFT" if payload.save_to_draft else "TEXT",
    )
    db.add(draft_message)
    db.commit()
    db.refresh(draft_message)

    logger.info(
        f"Shared AI response to conversation {conv_id} "
        f"by user {current_user.id}"
    )

    return ShareResponse(
        status="shared",
        message="AI response đã được chia sẻ vào ô nhập tin nhắn. Bạn có thể chỉnh sửa trước khi gửi.",
        conversation_id=payload.conversation_id,
        content=payload.content,
    )


# =============================================================================
# Additional Endpoints
# =============================================================================

@router.get("/intents")
def list_supported_intents() -> dict[str, Any]:
    """
    Lấy danh sách intents mà Copilot hỗ trợ.

    Useful cho frontend để hiển thị examples.
    """
    return {
        "intents": [
            {
                "name": "SEARCH",
                "description": "Tìm kiếm contacts",
                "examples": [
                    "Tìm người làm AI ở Hà Nội",
                    "Ai biết về blockchain?",
                    "Tìm founder startup",
                ],
            },
            {
                "name": "MEMORY",
                "description": "Hỏi về thông tin đã nhớ",
                "examples": [
                    "Người này là ai?",
                    "Họ làm ở đâu?",
                    "Chúng ta đã trao đổi gì?",
                ],
            },
            {
                "name": "REPLY_SUGGEST",
                "description": "Gợi ý trả lời",
                "examples": [
                    "Tôi nên nhắn gì?",
                    "Gợi ý reply cho người này",
                    "Viết giúp tôi một tin nhắn",
                ],
            },
            {
                "name": "RECOMMENDATION",
                "description": "Hỏi về gợi ý",
                "examples": [
                    "Ai cần follow-up?",
                    "Có gì mới không?",
                    "Ai nên ưu tiên?",
                ],
            },
            {
                "name": "TAG_SUGGEST",
                "description": "Gợi ý tags",
                "examples": [
                    "Gợi ý tags cho người này",
                    "Nên gắn nhãn gì?",
                ],
            },
            {
                "name": "CONNECTION",
                "description": "Hỏi về kết nối",
                "examples": [
                    "Ai phù hợp để giới thiệu?",
                    "Có người nào tương tự không?",
                ],
            },
        ]
    }
