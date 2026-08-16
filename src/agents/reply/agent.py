"""
Reply Suggestion Agent — Tự động phân tích tin nhắn gần nhất của đối phương và gợi ý câu trả lời phù hợp.
"""

import logging
import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.gateways.llm import LLMGateway
from src.models.chat import Conversation, Message
from src.models.user import User

logger = logging.getLogger(__name__)

REPLY_SUGGESTION_PROMPT = """Bạn là trợ lý AI thông minh hỗ trợ soạn thảo câu trả lời trong ứng dụng MemoryChat.

Nhiệm vụ của bạn là soạn 1 câu trả lời gợi ý (Smart Suggested Reply) tự nhiên, lịch sự, thân thiện và tinh tế nhất để [BẠN] phản hồi lại tin nhắn gần nhất của [ĐỐI PHƯƠNG] ({peer_name}).

Đoạn hội thoại gần đây:
{recent_conversation}

Tin nhắn gần nhất của [ĐỐI PHƯƠNG] ({peer_name}):
"{peer_last_message}"

Yêu cầu bắt buộc:
1. Trả lời đúng trọng tâm câu hỏi, đề nghị hoặc chia sẻ của đối phương.
2. Viết dưới ngôi xưng của [BẠN] (chủ tài khoản), giọng văn chuyên nghiệp, tự nhiên, nhã nhặn bằng tiếng Việt.
3. Độ dài ngắn gọn, súc tích (khoảng 1 - 2 câu, tối đa 3 câu).
4. CHỈ TRẢ VỀ DUY NHẤT nội dung câu trả lời, tuyệt đối không thêm lời dẫn, không bọc dấu ngoặc kép thừa.
"""


class ReplySuggestionAgent:
    """Agent gợi ý câu trả lời cho tin nhắn gần nhất của đối tác."""

    def __init__(self, llm: LLMGateway | None = None):
        self._llm = llm or LLMGateway()

    def generate_suggested_reply(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        db: Session,
    ) -> dict[str, Any]:
        """
        Tìm tin nhắn gần nhất của đối phương và sinh gợi ý câu trả lời.
        """
        conv = db.get(Conversation, conversation_id)
        if not conv:
            return {
                "peer_name": "Đối phương",
                "peer_last_message": None,
                "suggested_reply": "Chào bạn, mình rất vui được kết nối!",
                "created_at": None,
            }

        other_user_id = conv.user_b_id if str(conv.user_a_id) == str(user_id) else conv.user_a_id
        other_user = db.get(User, other_user_id)
        peer_name = other_user.full_name if other_user and other_user.full_name else (other_user.email if other_user else "Đối phương")

        # Tìm tin nhắn gần nhất mà đối phương đã gửi
        last_peer_msg = (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation_id,
                Message.sender_user_id != user_id,
            )
            .order_by(Message.created_at.desc())
            .first()
        )

        # Lấy 10 tin nhắn gần nhất để làm ngữ cảnh
        recent_messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(10)
            .all()
        )
        recent_messages.reverse()

        if not last_peer_msg:
            # Chưa có tin nhắn từ đối phương
            return {
                "peer_name": peer_name,
                "peer_last_message": None,
                "suggested_reply": f"Chào {peer_name}, mình rất vui được kết nối cùng bạn. Bạn có đang quan tâm đến chủ đề nào không?",
                "created_at": None,
            }

        conv_lines = []
        for msg in recent_messages:
            sender = "[BẠN]" if str(msg.sender_user_id) == str(user_id) else f"[ĐỐI PHƯƠNG ({peer_name})]"
            conv_lines.append(f"{sender}: {msg.content}")

        prompt = REPLY_SUGGESTION_PROMPT.format(
            recent_conversation="\n".join(conv_lines),
            peer_name=peer_name,
            peer_last_message=last_peer_msg.content,
        )

        try:
            raw_reply = self._llm.complete(prompt)
            # Clean quotes and whitespace
            suggested = raw_reply.strip().strip('"').strip("'").strip("`").strip()
            if not suggested:
                suggested = f"Chào {peer_name}, mình đã nhận được tin nhắn của bạn!"
        except Exception as e:
            logger.error(f"Error generating suggested reply: {e}")
            suggested = f"Chào {peer_name}, mình đã nhận được tin nhắn của bạn!"

        return {
            "peer_name": peer_name,
            "peer_last_message": last_peer_msg.content,
            "suggested_reply": suggested,
            "created_at": last_peer_msg.created_at.isoformat() if last_peer_msg.created_at else None,
        }
