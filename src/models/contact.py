import uuid
from typing import Optional

from sqlalchemy import String, Integer, JSON, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base, uuid_pk, created_at_col, updated_at_col

contact_tag_table = Table(
    "contact_tags",
    Base.metadata,
    Column("contact_id", ForeignKey("contacts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    created_at: Mapped[created_at_col]
    
    contacts = relationship("Contact", secondary=contact_tag_table, back_populates="tags")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    avatar: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    user = relationship("User", back_populates="contacts")
    memory = relationship("ContactMemory", back_populates="contact", uselist=False, cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="contact", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="contact", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=contact_tag_table, back_populates="contacts")


class ContactMemory(Base):
    __tablename__ = "contact_memories"

    id: Mapped[uuid_pk]
    contact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"), index=True, unique=True)
    summary: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    profession: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    interest: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    timeline: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    relationship_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # 0-100
    last_discussion: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    insights: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    updated_at: Mapped[updated_at_col]
    
    contact = relationship("Contact", back_populates="memory")
