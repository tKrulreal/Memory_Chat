"""
Contact and ContactMemory models.

Contact: Lưu thông tin về người liên hệ của một user.
ContactMemory: Lưu AI-extracted information về contact.
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base, created_at_col, updated_at_col, uuid_pk


class Contact(Base):
    """
    Người liên hệ của một user.

    Mỗi user có danh sách contacts riêng, không chia sẻ giữa các user.
    Contact được liên kết với một Conversation để track lịch sử chat.
    """
    __tablename__ = "contacts"

    id: Mapped[uuid_pk]
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("direct_conversations.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )

    # Basic info (có thể edit manual hoặc từ conversation)
    display_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # AI-extracted info (auto-updated by Memory Agent)
    profession: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Manual notes
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    # Metadata
    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    # Relationships
    owner = relationship("User", back_populates="contacts")
    conversation = relationship("Conversation")
    memory = relationship(
        "ContactMemory",
        back_populates="contact",
        uselist=False,
        cascade="all, delete-orphan"
    )
    recommendations = relationship(
        "Recommendation",
        foreign_keys="[Recommendation.contact_id]",
        back_populates="contact",
        cascade="all, delete-orphan"
    )
    target_recommendations = relationship(
        "Recommendation",
        foreign_keys="[Recommendation.target_contact_id]",
        back_populates="target_contact",
        cascade="all, delete-orphan",
    )

    def __init__(self, *args, **kwargs):
        if "user_id" in kwargs and "owner_user_id" not in kwargs:
            kwargs["owner_user_id"] = kwargs.pop("user_id")
        super().__init__(*args, **kwargs)

    @property
    def user_id(self):
        return self.owner_user_id

    @user_id.setter
    def user_id(self, value):
        self.owner_user_id = value




class ContactMemory(Base):
    """
    AI-generated memory về một contact.

    Memory được tạo tự động bởi Memory Agent từ conversation history.
    """
    __tablename__ = "contact_memories"

    id: Mapped[uuid_pk]
    contact_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contacts.id", ondelete="CASCADE"),
        index=True,
        unique=True
    )

    # Summary
    summary: Mapped[str | None] = mapped_column(String, nullable=True)

    # AI-extracted entities
    skills: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    interests: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Needs và Offers (cho Connection Recommendation)
    current_needs: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    current_offers: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Relationship scoring
    relationship_score: Mapped[int] = mapped_column(default=50)  # 0-100

    # Last interaction
    last_interaction: Mapped[datetime | None] = mapped_column(nullable=True)

    # Timeline (important events)
    timeline: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)

    # Follow-up tracking
    follow_up: Mapped[str | None] = mapped_column(String(512), nullable=True)
    last_met: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Metadata
    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    # Relationship
    contact = relationship("Contact", back_populates="memory")
