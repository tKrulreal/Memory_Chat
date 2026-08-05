from typing import Annotated
from datetime import datetime
import uuid

from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import create_engine

from src.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Types
uuid_pk = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]
str_255 = Annotated[str, mapped_column(String(255))]
created_at_col = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at_col = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=func.now())]

class Base(DeclarativeBase):
    pass
