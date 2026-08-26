from enum import StrEnum


class MessageRole(StrEnum):
    USER = "USER"
    CONTACT = "CONTACT"
    AI = "AI"


class ConversationStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class RecommendationType(StrEnum):
    FOLLOWUP = "FOLLOWUP"
    REPLY = "REPLY"
    PRIORITY = "PRIORITY"
    CONNECTION = "CONNECTION"
