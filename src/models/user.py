import uuid

from sqlalchemy import JSON, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base, created_at_col, updated_at_col, uuid_pk


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    # Relationships
    conversations_as_a = relationship("Conversation", foreign_keys="[Conversation.user_a_id]", back_populates="user_a", cascade="all, delete-orphan")
    conversations_as_b = relationship("Conversation", foreign_keys="[Conversation.user_b_id]", back_populates="user_b", cascade="all, delete-orphan")
    conversation_states = relationship("ConversationUserState", back_populates="user", cascade="all, delete-orphan")
    sent_messages = relationship("Message", back_populates="sender", cascade="all, delete-orphan")
    assistant_memories = relationship("AssistantMemory", back_populates="owner", cascade="all, delete-orphan")
    
    setting = relationship("Setting", back_populates="user", uselist=False, cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    event_logs = relationship("EventLog", back_populates="user", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="owner", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", foreign_keys="[Recommendation.owner_user_id]", back_populates="owner", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    profession: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    skills: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    interests: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    looking_for: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    offering: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    bio: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    user = relationship("User", back_populates="profile")




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
    results: Mapped[dict | None] = mapped_column(JSON, nullable=True)
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
