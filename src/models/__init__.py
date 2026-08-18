# Import order matters for SQLAlchemy relationships!
# 1. Base and database first
from src.models.database import Base, SessionLocal, engine

# 2. Models without foreign keys to other new tables
from src.models.ai import AssistantMemory, EventLog, OutboxEvent, Recommendation
from src.models.chat import Conversation, ConversationUserState, Message
from src.models.connection import ConnectionRequest

# 3. Models that are referenced by other models (Contact before User)
from src.models.contact import Contact, ContactMemory

# 4. Models that reference other models (User references Contact)
from src.models.user import Notification, SearchHistory, Setting, User

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "User",
    "Setting",
    "SearchHistory",
    "Notification",
    "Conversation",
    "ConversationUserState",
    "Message",
    "AssistantMemory",
    "OutboxEvent",
    "EventLog",
    "Recommendation",
    "Contact",
    "ContactMemory",
    "ConnectionRequest",
]
