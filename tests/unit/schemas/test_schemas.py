import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.models.chat import Conversation, Message
from src.models.contact import Contact
from src.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from src.schemas.conversation import ConversationResponse
from src.schemas.enums import MessageRole
from src.schemas.message import MessageCreate, MessageResponse
from src.schemas.pagination import PaginatedResponse, Pagination


def test_contact_validation():
    # Valid
    c = ContactCreate(name="Nguyễn Văn A")
    assert c.name == "Nguyễn Văn A"

    # Invalid (empty name)
    with pytest.raises(ValidationError):
        ContactCreate(name="")

    with pytest.raises(ValidationError):
        ContactCreate(name="   ")

    with pytest.raises(ValidationError):
        ContactUpdate(name="   ")


def test_message_validation():
    # Valid
    m = MessageCreate(content="Hello", role=MessageRole.USER)
    assert m.content == "Hello"

    # Invalid (empty content)
    with pytest.raises(ValidationError):
        MessageCreate(content="", role=MessageRole.USER)

    with pytest.raises(ValidationError):
        MessageCreate(content="   ", role=MessageRole.USER)


def test_contact_response_serializes_contact_model_fields():
    user_id = uuid.uuid4()
    contact = Contact(
        id=uuid.uuid4(),
        user_id=user_id,
        display_name="Nguyễn Văn A",
        avatar="https://example.com/avatar.png",
    )

    response = ContactResponse.model_validate(contact)

    assert response.name == "Nguyễn Văn A"
    assert response.avatar_url == "https://example.com/avatar.png"
    assert response.relationship_score == 0


def test_conversation_response_serializes_last_message_time():
    last_message_at = datetime.now(UTC)
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        contact_id=uuid.uuid4(),
        title="Chat với A",
        status="OPEN",
        last_message_time=last_message_at,
    )

    response = ConversationResponse.model_validate(conversation)

    assert response.last_message_at == last_message_at


def test_message_response_serializes_sender_type():
    created_at = datetime.now(UTC)
    message = Message(
        id=uuid.uuid4(),
        conversation_id=uuid.uuid4(),
        sender_type="USER",
        message_type="TEXT",
        content="Hello",
        created_at=created_at,
    )

    response = MessageResponse.model_validate(message)

    assert response.role is MessageRole.USER
    assert response.content == "Hello"


def test_paginated_response_validates_metadata():
    response = PaginatedResponse[str](
        data=["contact"],
        pagination=Pagination(page=1, limit=20, total=1),
    )

    assert response.model_dump() == {
        "data": ["contact"],
        "pagination": {"page": 1, "limit": 20, "total": 1},
    }

    with pytest.raises(ValidationError):
        Pagination(page=0, limit=20, total=1)
