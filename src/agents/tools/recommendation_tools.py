"""
Recommendation tools cho AI Agents.

Dùng LangChain @tool decorator.
"""

import logging
import uuid
from typing import Annotated

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from src.gateways.llm import LLMGateway
from src.models.ai import Recommendation
from src.models.contact import Contact, ContactMemory
from src.models.database import SessionLocal

logger = logging.getLogger(__name__)


def _get_db() -> Session:
    return SessionLocal()


def _get_llm() -> LLMGateway:
    return LLMGateway()


@tool
def get_recommendations(
    user_id: Annotated[str, "UUID của user hiện tại (bắt buộc để enforce access control)"],
    status: Annotated[str, "Trạng thái: PENDING, ACCEPTED, REJECTED"] = "PENDING",
    limit: Annotated[int, "Số lượng tối đa"] = 10,
) -> str:
    """
    Lấy danh sách recommendations cho user hiện tại.

    Recommendation là các gợi ý hành động được AI sinh ra tự động:
    - FOLLOWUP: Nên hỏi thăm vì lâu chưa liên hệ
    - REPLY: Nên trả lời tin nhắn vì họ đang đợi
    - PRIORITY: Đây là liên hệ quan trọng
    - TAG: Gợi ý tag mới
    - CONNECTION: Gợi ý kết nối hai người

    Args:
        user_id: UUID của user hiện tại (bắt buộc!)
        status: Lọc theo trạng thái (mặc định PENDING)
        limit: Số lượng tối đa trả về

    Returns:
        Danh sách recommendations dạng text
    """
    db = _get_db()
    try:
        # Validate user_id
        try:
            uid = uuid.UUID(user_id)
        except ValueError:
            return f"Invalid user_id: {user_id}"

        from sqlalchemy import desc, select
        from src.models.user import User

        # ✅ FIX: Lọc theo owner_user_id để ngăn data leak
        stmt = (
            select(Recommendation, User.full_name)
            .outerjoin(User, Recommendation.target_user_id == User.id)
            .where(Recommendation.owner_user_id == uid)
            .where(Recommendation.status == status)
            .order_by(desc(Recommendation.created_at))
            .limit(limit)
        )

        results = db.execute(stmt).all()

        if not results:
            return "Không có recommendation nào."

        lines = [f"=== {len(results)} Recommendations ({status}) ==="]
        for rec, contact_name in results:
            priority_emoji = {
                "HIGH": "🔴",
                "MEDIUM": "🟡",
                "LOW": "🟢",
            }.get(rec.priority, "⚪")

            type_labels = {
                "FOLLOWUP": "📞 Follow-up",
                "REPLY": "💬 Cần trả lời",
                "PRIORITY": "⭐ Ưu tiên",
                "TAG": "🏷️ Gợi ý tag",
                "CONNECTION": "🔗 Kết nối",
            }.get(rec.type, f"📌 {rec.type}")

            lines.append(
                f"\n{priority_emoji} {type_labels}\n"
                f"   👤 {contact_name}\n"
                f"   💭 {rec.reason}\n"
                f"   📅 {rec.created_at.strftime('%d/%m/%Y %H:%M') if rec.created_at else 'N/A'}"
            )

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"get_recommendations failed: {e}")
        return f"Lỗi khi lấy recommendations: {str(e)}"
    finally:
        db.close()


@tool
def recommend_reply(
    contact_id: Annotated[str, "UUID của contact cần gợi ý reply"],
    context: Annotated[str, "Ngữ cảnh bổ sung (tùy chọn)"] = "",
) -> str:
    """
    Gợi ý một câu trả lời phù hợp cho contact.

    Dựa trên memory và cuộc trò chuyện gần nhất,
    LLM sẽ đề xuất một câu reply tự nhiên.

    Args:
        contact_id: UUID string của contact
        context: Ngữ cảnh bổ sung (tuỳ chọn)

    Returns:
        Gợi ý câu trả lời dạng text
    """
    db = _get_db()
    try:
        cid = uuid.UUID(contact_id)
    except ValueError:
        return f"Invalid contact_id: {contact_id}"

    try:
        # Get contact info
        contact = db.get(Contact, cid)
        if not contact:
            return f"Không tìm thấy contact {contact_id}"

        # Get memory
        memory = db.query(ContactMemory).filter(
            ContactMemory.contact_id == cid
        ).first()

        # Get recent messages
        from sqlalchemy import select

        from src.models.chat import Conversation, Message

        ua_id, ub_id = sorted([contact.user_id, contact.contact_user_id])
        conv = db.query(Conversation).filter(Conversation.user_a_id == ua_id, Conversation.user_b_id == ub_id).first()
        messages = []
        if conv:
            stmt = (
                select(Message)
                .where(Message.conversation_id == conv.id)
                .order_by(Message.created_at.desc())
                .limit(10)
            )
            messages = list(reversed(db.scalars(stmt).all()))

        # Build context string
        conversation_text = "\n".join([
            f"{'[BẠN]' if m.sender_user_id == contact.user_id else f'[{contact.display_name}]'} {m.content}"
            for m in messages
        ])

        # Build prompt for LLM
        system_prompt = """Bạn là một trợ lý AI viết tin nhắn.
Nhiệm vụ của bạn là gợi ý một câu trả lời tự nhiên, thân thiện phù hợp với:
- Phong cách giao tiếp đã học được từ cuộc trò chuyện
- Ngữ cảnh về contact (nghề nghiệp, công ty, sở thích)
- Nội dung cuộc trò chuyện gần nhất

Chỉ trả về MỘT câu reply ngắn gọn (dưới 50 từ), không cần giải thích."""

        memory_context = ""
        if memory:
            # Unwrap dict if skills/interest are stored as {"skills": [...]} or {"interests": [...]}
            interests_list = []
            if memory.interest:
                if isinstance(memory.interest, dict):
                    interests_list = memory.interest.get("interests", [])
                elif isinstance(memory.interest, list):
                    interests_list = memory.interest
            memory_context = f"""
Thông tin về contact:
- Tên: {contact.display_name}
- Nghề nghiệp: {memory.profession or 'Chưa biết'}
- Công ty: {memory.company or 'Chưa biết'}
- Sở thích: {', '.join(interests_list) if interests_list else 'Chưa biết'}
"""

        user_prompt = f"""Cuộc trò chuyện gần đây:
{conversation_text}

{memory_context}

Ngữ cảnh bổ sung: {context if context else 'Không có'}

Viết một câu reply phù hợp:"""

        llm = _get_llm()
        reply = llm.chat(system_prompt, user_prompt).strip()

        return f"Gợi ý reply cho {contact.display_name}:\n\n{reply}"

    except Exception as e:
        logger.error(f"recommend_reply failed: {e}")
        return f"Lỗi khi gợi ý reply: {str(e)}"
    finally:
        db.close()
