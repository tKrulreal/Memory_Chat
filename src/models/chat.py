import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base, created_at_col, updated_at_col, uuid_pk


class Conversation(Base):
    __tablename__ = "direct_conversations"
    __table_args__ = (
        UniqueConstraint("user_a_id", "user_b_id", name="uq_direct_conversation"),
        CheckConstraint("user_a_id < user_b_id", name="chk_user_order"),
    )

    id: Mapped[uuid_pk]
    user_a_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    user_b_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    type: Mapped[str] = mapped_column(String(50), default="P2P")
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_message_content: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    last_message_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    user_a = relationship("User", foreign_keys=[user_a_id], back_populates="conversations_as_a")
    user_b = relationship("User", foreign_keys=[user_b_id], back_populates="conversations_as_b")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    user_states = relationship("ConversationUserState", back_populates="conversation", cascade="all, delete-orphan")


class ConversationUserState(Base):
    __tablename__ = "conversation_user_state"

    id: Mapped[uuid_pk]
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("direct_conversations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    role: Mapped[str] = mapped_column(String(50), default="MEMBER")
    last_read_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    is_muted: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[created_at_col]

    updated_at: Mapped[updated_at_col]

    conversation = relationship("Conversation", back_populates="user_states")
    user = relationship("User", back_populates="conversation_states")


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint("sender_user_id", "client_message_id", name="uq_client_message_id"),
        Index("ix_messages_conv_created_id", "conversation_id", "created_at", "id"),
    )

    id: Mapped[uuid_pk]
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("direct_conversations.id", ondelete="CASCADE"), index=True)
    sender_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    client_message_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    reply_to_message_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)

    content: Mapped[str] = mapped_column(String)
    message_type: Mapped[str] = mapped_column(String(50))  # TEXT, SYSTEM, v.v.

    created_at: Mapped[created_at_col]
    edited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")
    reactions = relationship("MessageReaction", back_populates="message", cascade="all, delete-orphan")


class MessageReaction(Base):
    __tablename__ = "message_reactions"
    __table_args__ = (
        UniqueConstraint("message_id", "user_id", "emoji", name="uq_message_user_emoji"),
    )

    id: Mapped[uuid_pk]
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    emoji: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[created_at_col]

    message = relationship("Message", back_populates="reactions")
    user = relationship("User", back_populates="message_reactions")
