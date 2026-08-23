import sys
import uuid
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup engine
db_url = "postgresql://postgres:postgres@localhost:5433/p214_db"
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
db = Session()

from src.models.user import User
from src.models.tag import Tag

users = db.query(User).all()
for u in users:
    print(f"User: {u.email} ({u.id})")
    tags = db.query(Tag).filter(Tag.user_id == u.id).all()
    print("  Tags:", [t.name for t in tags])

db.close()
