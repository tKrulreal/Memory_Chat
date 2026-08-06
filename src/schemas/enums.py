from enum import Enum

class MessageRole(str, Enum):
    USER = "USER"
    CONTACT = "CONTACT"
    AI = "AI"

class ConversationStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"
