import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base, created_at_col, updated_at_col, uuid_pk


class ConnectionRequest(Base):
    __tablename__ = "connection_requests"
    __table_args__ = (
        UniqueConstraint("sender_id", "receiver_id", name="uq_connection_request"),
    )

    id: Mapped[uuid_pk]
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    receiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Status can be PENDING, ACCEPTED, REJECTED, CANCELLED
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True)

    created_at: Mapped[created_at_col]
    updated_at: Mapped[updated_at_col]

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
