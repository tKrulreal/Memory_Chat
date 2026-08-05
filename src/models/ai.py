import uuid
from typing import Optional

from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base, uuid_pk, created_at_col

class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid_pk]
    contact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"), index=True)
    
    type: Mapped[str] = mapped_column(String(50)) # FOLLOWUP, REPLY, TAG, MERGE, CONNECTION, PRIORITY
    reason: Mapped[str] = mapped_column(String(1024))
    priority: Mapped[str] = mapped_column(String(50), default="MEDIUM") # HIGH, MEDIUM, LOW
    status: Mapped[str] = mapped_column(String(50), default="PENDING") # PENDING, ACCEPTED, REJECTED
    
    created_at: Mapped[created_at_col]
    
    contact = relationship("Contact", back_populates="recommendations")


class EventLog(Base):
    __tablename__ = "event_logs"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    event_type: Mapped[str] = mapped_column(String(50)) # OPEN_CHAT, SEND_MESSAGE, SEARCH, etc.
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[created_at_col]
    
    user = relationship("User", back_populates="event_logs")
    conversation = relationship("Conversation", back_populates="event_logs")
