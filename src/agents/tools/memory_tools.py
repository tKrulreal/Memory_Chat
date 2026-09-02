"""
Memory tools cho AI Agents.

Dùng LangChain @tool decorator.
"""

import logging
import uuid
from typing import Annotated

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from src.models.chat import Conversation, Message
from src.models.contact import ContactMemory
from src.models.database import SessionLocal

logger = logging.getLogger(__name__)


def _get_db() -> Session:
    return SessionLocal()


@tool
def get_contact_memory(
    user_id: Annotated[str, "UUID của user hiện tại (bắt buộc)"],
    contact_id: Annotated[str, "UUID của contact cần lấy memory"],
) -> str:
    """
    Lấy toàn bộ memory của một contact.

    Bao gồm: summary, company, profession, skills, interests,
    timeline, relationship_score, insights.

    Args:
        user_id: UUID của user hiện tại (bắt buộc để enforce access)
        contact_id: UUID string của contact

    Returns:
        Thông tin memory dạng text
    """
    db = _get_db()
    try:
        # Validate user_id
        try:
            uid = uuid.UUID(user_id)
        except ValueError:
            return f"Invalid user_id: {user_id}"

        # Validate contact_id
        try:
            cid = uuid.UUID(contact_id)
        except ValueError:
            return f"Invalid contact_id: {contact_id}"

        # Verify ownership: contact belongs to user
        from src.models.contact import Contact
        contact = db.get(Contact, cid)
        if not contact:
            return f"Không tìm thấy contact {contact_id}"
        if contact.user_id != uid:
            return f"Không có quyền truy cập contact {contact_id}"

        memory = db.query(ContactMemory).filter(
            ContactMemory.contact_id == cid
        ).first()

        if not memory:
            return f"Chưa có memory cho contact {contact_id}"

        # Build readable output
        lines = [f"=== Memory của Contact {contact_id} ==="]

        if memory.summary:
            lines.append(f"\n📝 Tóm tắt:\n{memory.summary}")

        if memory.profession:
            lines.append(f"\n💼 Nghề nghiệp: {memory.profession}")

        if memory.company:
            lines.append(f"\n🏢 Công ty: {memory.company}")

        if memory.skills:
            skills_list = memory.skills if isinstance(memory.skills, list) else list(memory.skills)
            lines.append(f"\n🛠 Kỹ năng: {', '.join(skills_list)}")

        if memory.interest:
            interests_list = memory.interest if isinstance(memory.interest, list) else list(memory.interest)
            lines.append(f"\n🎯 Sở thích: {', '.join(interests_list)}")

        facts = memory.facts if isinstance(memory.facts, dict) else {}

        timeline = facts.get("timeline") or getattr(memory, "timeline", None)
        if timeline:
            lines.append(f"\n📅 Timeline: {timeline}")

        rel_score = facts.get("relationship_score") if facts.get("relationship_score") is not None else getattr(memory, "relationship_score", None)
        if rel_score is not None:
            emoji = "❤️" if rel_score >= 80 else "🤝" if rel_score >= 50 else "👋"
            lines.append(f"\n{emoji} Điểm quan hệ: {rel_score}/100")

        last_discussion = facts.get("last_discussion") or getattr(memory, "last_discussion", None)
        if last_discussion:
            lines.append(f"\n💬 Cuộc trò chuyện gần nhất:\n{last_discussion}")

        insights = facts.get("insights") or getattr(memory, "insights", None)
        if insights:
            lines.append("\n💡 Insights:")
            for insight in (insights if isinstance(insights, list) else [insights]):
                if isinstance(insight, dict):
                    lines.append(f"  - [{insight.get('type', 'INFO')}] {insight.get('description', '')}")

        if memory.updated_at:
            lines.append(f"\n⏰ Cập nhật lần cuối: {memory.updated_at.strftime('%d/%m/%Y %H:%M')}")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"get_contact_memory failed: {e}")
        return f"Lỗi khi lấy memory: {str(e)}"
    finally:
        db.close()


@tool
def get_recent_messages(
    user_id: Annotated[str, "UUID của user hiện tại (bắt buộc)"],
    conversation_id: Annotated[str, "UUID của conversation"],
    limit: Annotated[int, "Số tin nhắn cần lấy"] = 10,
) -> str:
    """
    Lấy các tin nhắn gần nhất của một conversation.

    Args:
        user_id: UUID của user hiện tại (bắt buộc để enforce access)
        conversation_id: UUID string của conversation
        limit: Số tin nhắn cần lấy (mặc định 10)

    Returns:
        Danh sách tin nhắn dạng text
    """
    db = _get_db()
    try:
        # Validate user_id
        try:
            uid = uuid.UUID(user_id)
        except ValueError:
            return f"Invalid user_id: {user_id}"

        # Validate conversation_id
        try:
            cid = uuid.UUID(conversation_id)
        except ValueError:
            return f"Invalid conversation_id: {conversation_id}"

        # Verify ownership: user is either user_a or user_b
        conv = db.get(Conversation, cid)
        if not conv:
            return f"Không tìm thấy conversation {conversation_id}"
        if conv.user_a_id != uid and conv.user_b_id != uid:
            return f"Không có quyền truy cập conversation {conversation_id}"

        # Fetch messages
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == cid)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )

        if not messages:
            return f"Không có tin nhắn trong conversation {conversation_id}"

        # Reverse to show oldest first
        messages = list(reversed(messages))

        # Get peer name if possible
        peer_id = conv.user_b_id if conv.user_a_id == uid else conv.user_a_id
        from src.models.user import User
        peer_user = db.get(User, peer_id)
        peer_name = peer_user.full_name if (peer_user and peer_user.full_name) else (peer_user.email if peer_user else "Đối tác")

        lines = [f"=== {len(messages)} tin nhắn gần nhất trong đoạn chat ==="]
        for msg in messages:
            is_me = (msg.sender_user_id == uid)
            sender = "👤 BẠN (Tôi)" if is_me else f"💬 {peer_name}"
            time_str = msg.created_at.strftime("%d/%m %H:%M") if msg.created_at else ""
            content_preview = msg.content[:300] + "..." if len(msg.content) > 300 else msg.content
            lines.append(f"\n{sender} [{time_str}]:\n{content_preview}")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"get_recent_messages failed: {e}")
        return f"Lỗi khi lấy messages: {str(e)}"
    finally:
        db.close()
