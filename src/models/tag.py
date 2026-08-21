import uuid
from sqlalchemy import Boolean, ForeignKey, String, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base, created_at_col, updated_at_col, uuid_pk


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]
    
    # Relationships
    users = relationship("UserTag", back_populates="tag", cascade="all, delete-orphan")


class UserTag(Base):
    __tablename__ = "user_tags"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), index=True)

    created_at: Mapped[created_at_col]

    __table_args__ = (
        UniqueConstraint("user_id", "tag_id", name="uq_user_tag"),
    )

    # Relationships
    tag = relationship("Tag", back_populates="users")


class AISystemConfig(Base):
    __tablename__ = "ai_system_config"

    id: Mapped[uuid_pk]
    key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    value: Mapped[dict] = mapped_column(JSON)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]
