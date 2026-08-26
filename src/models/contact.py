"""
Contact and ContactMemory models matching database schema.
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from src.models.database import Base, created_at_col, updated_at_col, uuid_pk


class Contact(Base):
    """
    Liên hệ của một user trong hệ thống.
    """
    __tablename__ = "contacts"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    contact_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    created_at: Mapped[created_at_col]

    owner_user_id = synonym("user_id")

    user = relationship("User", foreign_keys=[user_id], back_populates="contacts")
    contact_user = relationship("User", foreign_keys=[contact_user_id])

    @property
    def display_name(self) -> str:
        return self.contact_user.full_name if (self.contact_user and self.contact_user.full_name) else (self.contact_user.email if self.contact_user else "")

    @property
    def profession(self) -> str | None:
        return self.contact_user.profile.profession if (self.contact_user and self.contact_user.profile) else None

    @property
    def company(self) -> str | None:
        return self.contact_user.profile.company if (self.contact_user and self.contact_user.profile) else None


class ContactMemory(Base):
    """
    AI-generated memory về một contact.
    """
    __tablename__ = "contact_memories"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    contact_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    summary: Mapped[str | None] = mapped_column(String, nullable=True)
    facts: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    contact_id = synonym("contact_user_id")

    user = relationship("User", foreign_keys=[user_id])
    contact_user = relationship("User", foreign_keys=[contact_user_id])

    @property
    def profession(self) -> str | None:
        return self.contact_user.profile.profession if (self.contact_user and self.contact_user.profile) else None

    @property
    def company(self) -> str | None:
        return self.contact_user.profile.company if (self.contact_user and self.contact_user.profile) else None

    @property
    def skills(self) -> list | None:
        return self.contact_user.profile.skills if (self.contact_user and self.contact_user.profile) else None

    @property
    def interest(self) -> list | None:
        return self.contact_user.profile.interests if (self.contact_user and self.contact_user.profile) else None
