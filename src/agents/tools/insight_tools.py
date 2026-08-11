"""
Insight tools cho AI Agents.

Dùng LangChain @tool decorator.
"""

import logging
import uuid
from typing import Annotated

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from src.models.database import SessionLocal
from src.models.contact import ContactMemory

logger = logging.getLogger(__name__)


def _get_db() -> Session:
    return SessionLocal()


@tool
def get_contact_insights(
    contact_id: Annotated[str, "UUID của contact cần lấy insights"],
) -> str:
    """
    Lấy các insights (hiểu biết sâu) về một contact.

    Insights được AI sinh ra từ phân tích behavior và conversation pattern:
    - INTEREST_PATTERN: Xu hướng quan tâm (VD: "Thường xuyên nhắc đến AI")
    - COMMUNICATION_STYLE: Phong cách giao tiếp (VD: "Thích nhắn tin ngắn gọn")
    - RELATIONSHIP_TREND: Xu hướng mối quan hệ (VD: "Điểm quan hệ đang tăng")

    Args:
        contact_id: UUID string của contact

    Returns:
        Danh sách insights dạng text
    """
    db = _get_db()
    try:
        cid = uuid.UUID(contact_id)
    except ValueError:
        return f"Invalid contact_id: {contact_id}"

    try:
        memory = db.query(ContactMemory).filter(
            ContactMemory.contact_id == cid
        ).first()

        if not memory:
            return f"Chưa có memory cho contact {contact_id}"

        if not memory.insights:
            return f"Chưa có insights cho contact {contact_id}. Có thể cần chạy refresh insight trước."

        type_labels = {
            "INTEREST_PATTERN": "🎯 Xu hướng quan tâm",
            "COMMUNICATION_STYLE": "💬 Phong cách giao tiếp",
            "RELATIONSHIP_TREND": "📈 Xu hướng quan hệ",
        }

        lines = [f"=== Insights cho contact {contact_id} ==="]
        for insight in (memory.insights if isinstance(memory.insights, list) else [memory.insights]):
            if isinstance(insight, dict):
                insight_type = insight.get("type", "INFO")
                description = insight.get("description", "")
                label = type_labels.get(insight_type, f"📌 {insight_type}")
                lines.append(f"\n{label}:")
                lines.append(f"   {description}")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"get_contact_insights failed: {e}")
        return f"Lỗi khi lấy insights: {str(e)}"
    finally:
        db.close()
