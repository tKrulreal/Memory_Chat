import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, ForeignKey, String, DateTime, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base, created_at_col, updated_at_col, uuid_pk


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)

    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_ai: Mapped[bool] = mapped_column(Boolean, default=False)

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
    message_reactions = relationship("MessageReaction", back_populates="user", cascade="all, delete-orphan")
    blocked_users = relationship("UserBlock", foreign_keys="[UserBlock.blocker_id]", back_populates="blocker", cascade="all, delete-orphan")
    blocked_by = relationship("UserBlock", foreign_keys="[UserBlock.blocked_id]", back_populates="blocked", cascade="all, delete-orphan")


class UserBlock(Base):
    __tablename__ = "user_blocks"
    __table_args__ = (
        UniqueConstraint("blocker_id", "blocked_id", name="uq_user_block"),
    )

    id: Mapped[uuid_pk]
    blocker_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    blocked_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    created_at: Mapped[created_at_col]

    blocker = relationship("User", foreign_keys=[blocker_id], back_populates="blocked_users")
    blocked = relationship("User", foreign_keys=[blocked_id], back_populates="blocked_by")


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
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    github: Mapped[str | None] = mapped_column(String(255), nullable=True)
    linkedin: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    education: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)

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
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    ai_read_profile: Mapped[bool] = mapped_column(Boolean, default=True)
    ai_extract_chat: Mapped[bool] = mapped_column(Boolean, default=True)
    sound_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    enter_is_send: Mapped[bool] = mapped_column(Boolean, default=True)
    read_receipts: Mapped[bool] = mapped_column(Boolean, default=True)
    online_status: Mapped[bool] = mapped_column(Boolean, default=True)
    media_auto_download: Mapped[bool] = mapped_column(Boolean, default=True)
    message_preview: Mapped[bool] = mapped_column(Boolean, default=True)
    accent_color: Mapped[str] = mapped_column(String(50), default="blue")
    font_size: Mapped[str] = mapped_column(String(50), default="medium")
    ai_memory_refresh_interval: Mapped[str] = mapped_column(String(50), default="realtime")
    ai_memory_window: Mapped[str] = mapped_column(String(50), default="unlimited")
    ai_recommendation_interval: Mapped[str] = mapped_column(String(50), default="24h")
    ai_copilot_context_turns: Mapped[int] = mapped_column(Integer, default=10)

    @property
    def notifications_enabled(self) -> bool:
        return self.notification

    @notifications_enabled.setter
    def notifications_enabled(self, value: bool) -> None:
        self.notification = value

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
    type: Mapped[str] = mapped_column(String(50)) # RECOMMENDATION, MATCH_SUGGESTION, CONNECTION_REQUEST, CONNECTION_ACCEPTED
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(String(2048))
    status: Mapped[str] = mapped_column(String(50), default="UNREAD") # UNREAD, READ
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[created_at_col]

    user = relationship("User", back_populates="notifications")
