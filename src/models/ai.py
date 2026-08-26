import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from src.models.database import Base, created_at_col, updated_at_col, uuid_pk


class Recommendation(Base):
    """
    Recommendation model cho tất cả các loại recommendations.

    Types:
    - FOLLOWUP: Nên hỏi thăm vì lâu chưa liên hệ
    - REPLY: Nên trả lời tin nhắn vì họ đang đợi
    - PRIORITY: Đây là liên hệ quan trọng
    - CONNECTION: Gợi ý kết nối hai người
    """
    __tablename__ = "recommendations"

    id: Mapped[uuid_pk]
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    target_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )

    type: Mapped[str] = mapped_column(String(50))  # FOLLOWUP, REPLY, PRIORITY, CONNECTION
    status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PENDING, ACCEPTED, REJECTED, DISMISSED
    reason: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence = synonym("match_score")
    priority: Mapped[str | None] = mapped_column(String(50), default="MEDIUM", nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    # Relationships
    owner = relationship("User", foreign_keys=[owner_user_id], back_populates="recommendations")
    target_user = relationship("User", foreign_keys=[target_user_id])




class EventLog(Base):
    __tablename__ = "event_logs"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("direct_conversations.id", ondelete="SET NULL"), nullable=True, index=True)

    event_type: Mapped[str] = mapped_column(String(50)) # OPEN_CHAT, NEW_MESSAGE, SEARCH, etc.
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[created_at_col]

    user = relationship("User", back_populates="event_logs")
    conversation = relationship("Conversation")


class AssistantMemory(Base):
    __tablename__ = "assistant_memories"

    id: Mapped[uuid_pk]
    owner_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("direct_conversations.id", ondelete="CASCADE"), index=True)

    scope: Mapped[str] = mapped_column(String(50), default="CONVERSATION")  # CONVERSATION, GLOBAL, CONTACT
    through_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    summary: Mapped[str | None] = mapped_column(String, nullable=True)
    facts: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    owner = relationship("User", back_populates="assistant_memories")
    conversation = relationship("Conversation")


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[uuid_pk]
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True) # PENDING, PROCESSED, FAILED
    
    created_at: Mapped[created_at_col]


class CopilotMessage(Base):
    """
    Lưu trữ lịch sử hội thoại Copilot giữa user và AI.
    """
    __tablename__ = "copilot_messages"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    role: Mapped[str] = mapped_column(String(20))  # "user" | "assistant"
    content: Mapped[str] = mapped_column(String)
    tools_used: Mapped[list | None] = mapped_column(JSON, nullable=True)
    sources: Mapped[list | None] = mapped_column(JSON, nullable=True)
    intent: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    user = relationship("User")
