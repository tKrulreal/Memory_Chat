import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import String, create_engine, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, sessionmaker

from src.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Types
uuid_pk = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]
str_255 = Annotated[str, mapped_column(String(255))]
created_at_col = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at_col = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=func.now())]

class Base(DeclarativeBase):
    pass
