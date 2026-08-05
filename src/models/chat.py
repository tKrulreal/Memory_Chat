import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base, uuid_pk, created_at_col, updated_at_col


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    contact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"), index=True)
    
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_message: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    last_message_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="OPEN") # OPEN, CLOSED, ARCHIVED
    
    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    user = relationship("User", back_populates="conversations")
    contact = relationship("Contact", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    event_logs = relationship("EventLog", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid_pk]
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    sender_type: Mapped[str] = mapped_column(String(50)) # USER, CONTACT
    content: Mapped[str] = mapped_column(String)
    message_type: Mapped[str] = mapped_column(String(50)) # TEXT, AI, SYSTEM
    
    created_at: Mapped[created_at_col]
    
    conversation = relationship("Conversation", back_populates="messages")
