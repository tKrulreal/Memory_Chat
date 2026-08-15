import uuid

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base, created_at_col, updated_at_col, uuid_pk


class EventLog(Base):
    __tablename__ = "event_logs"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("direct_conversations.id", ondelete="SET NULL"), nullable=True, index=True)

    event_type: Mapped[str] = mapped_column(String(50)) # OPEN_CHAT, SEND_MESSAGE, SEARCH, etc.
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[created_at_col]

    user = relationship("User", back_populates="event_logs")
    conversation = relationship("Conversation")


class AssistantMemory(Base):
    __tablename__ = "assistant_memories"

    id: Mapped[uuid_pk]
    owner_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("direct_conversations.id", ondelete="CASCADE"), index=True)
    
    through_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    summary: Mapped[str | None] = mapped_column(String, nullable=True)
    facts: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
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
