import uuid
from typing import Optional

from sqlalchemy import String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base, uuid_pk, str_255, created_at_col, updated_at_col


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    
    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]
    
    # Relationships
    contacts = relationship("Contact", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    setting = relationship("Setting", back_populates="user", uselist=False, cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    event_logs = relationship("EventLog", back_populates="user", cascade="all, delete-orphan")


class Setting(Base):
    __tablename__ = "settings"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    auto_tag: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_memory: Mapped[bool] = mapped_column(Boolean, default=True)
    theme: Mapped[str] = mapped_column(String(50), default="system")
    language: Mapped[str] = mapped_column(String(50), default="vi")
    notification: Mapped[bool] = mapped_column(Boolean, default=True)
    
    user = relationship("User", back_populates="setting")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    query: Mapped[str] = mapped_column(String(1024))
    results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    result_count: Mapped[int] = mapped_column(default=0)
    
    created_at: Mapped[created_at_col]

    user = relationship("User", back_populates="search_history")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(50)) # RECOMMENDATION, FOLLOWUP, MEMORY_UPDATED
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(String(2048))
    status: Mapped[str] = mapped_column(String(50), default="UNREAD") # UNREAD, READ
    
    created_at: Mapped[created_at_col]
    
    user = relationship("User", back_populates="notifications")
