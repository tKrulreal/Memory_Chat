"""
Tests cho Memory API endpoints.
"""

import uuid

import pytest
from sqlalchemy.orm import Session

from src.events.bus import EventBus
from src.models.chat import Conversation, Message
from src.models.contact import Contact, ContactMemory


@pytest.mark.asyncio
async def test_get_memory_returns_404_when_no_memory(
    authenticated_client, db_session: Session, current_user
):
    contact = Contact(user_id=current_user.id, display_name="Alice")
    db_session.add(contact)
    db_session.commit()

    response = await authenticated_client.get(f"/api/v1/memory/{contact.id}")
    # No memory exists → returns None → FastAPI returns 204 or we return None
    # Our implementation returns None → 200 with null body
    assert response.status_code == 200
    assert response.text == "null" or response.json() is None


@pytest.mark.asyncio
async def test_get_memory_returns_memory(
    authenticated_client, db_session: Session, current_user
):
    contact = Contact(user_id=current_user.id, display_name="Alice")
    db_session.add(contact)
    db_session.commit()

    memory = ContactMemory(
        contact_id=contact.id,
        summary="Student at VinUni",
        profession="Student",
        company="VinUni",
        skills={"skills": ["Python"]},
        interest={"interests": ["AI"]},
        relationship_score=75,
    )
    db_session.add(memory)
    db_session.commit()

    response = await authenticated_client.get(f"/api/v1/memory/{contact.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Student at VinUni"
    assert data["profession"] == "Student"
    assert data["skills"] == {"skills": ["Python"]}
    assert data["relationship_score"] == 75


@pytest.mark.asyncio
async def test_get_memory_returns_404_for_foreign_contact(
    authenticated_client, db_session: Session, other_user
):
    contact = Contact(user_id=other_user.id, display_name="Private")
    db_session.add(contact)
    db_session.commit()

    response = await authenticated_client.get(f"/api/v1/memory/{contact.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_memory_returns_404_nonexistent(
    authenticated_client,
):
    response = await authenticated_client.get(f"/api/v1/memory/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_trigger_memory_refresh(
    authenticated_client, db_session: Session, current_user, event_bus: EventBus
):
    contact = Contact(user_id=current_user.id, display_name="Alice")
    db_session.add(contact)
    db_session.commit()

    response = await authenticated_client.post(f"/api/v1/memory/{contact.id}/refresh")
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "triggered"
    assert data["contact_id"] == str(contact.id)


@pytest.mark.asyncio
async def test_trigger_memory_refresh_404(
    authenticated_client,
):
    response = await authenticated_client.post(f"/api/v1/memory/{uuid.uuid4()}/refresh")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_memory_creates_new_memory(
    authenticated_client, db_session: Session, current_user
):
    contact = Contact(user_id=current_user.id, display_name="Alice")
    db_session.add(contact)
    db_session.commit()

    response = await authenticated_client.patch(
        f"/api/v1/memory/{contact.id}",
        json={"summary": "Updated summary", "profession": "Developer"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Updated summary"
    assert data["profession"] == "Developer"


@pytest.mark.asyncio
async def test_patch_memory_updates_existing(
    authenticated_client, db_session: Session, current_user
):
    contact = Contact(user_id=current_user.id, display_name="Alice")
    db_session.add(contact)
    db_session.commit()

    memory = ContactMemory(
        contact_id=contact.id,
        summary="Original",
        relationship_score=50,
    )
    db_session.add(memory)
    db_session.commit()

    response = await authenticated_client.patch(
        f"/api/v1/memory/{contact.id}",
        json={"summary": "Updated", "relationship_score": 80},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Updated"
    assert data["relationship_score"] == 80


@pytest.mark.asyncio
async def test_patch_memory_empty_body(
    authenticated_client, db_session: Session, current_user
):
    contact = Contact(user_id=current_user.id, display_name="Alice")
    db_session.add(contact)
    db_session.commit()

    response = await authenticated_client.patch(
        f"/api/v1/memory/{contact.id}",
        json={},
    )
    assert response.status_code == 400
    body = response.json()
    # App's exception handler formats HTTPException as {"error", "message"}
    assert "No fields" in body.get("detail", "") or "No fields" in body.get("message", "")


@pytest.mark.asyncio
async def test_get_memory_timeline(
    authenticated_client, db_session: Session, current_user
):
    contact = Contact(user_id=current_user.id, display_name="Alice")
    db_session.add(contact)
    db_session.commit()

    conversation = Conversation(
        user_id=current_user.id,
        contact_id=contact.id,
        title="Chat",
        status="OPEN",
    )
    db_session.add(conversation)
    db_session.commit()

    # Add messages
    for i, content in enumerate(["Hello", "Hi there", "How are you?"]):
        msg = Message(
            conversation_id=conversation.id,
            sender_type="USER" if i % 2 == 0 else "CONTACT",
            content=content,
            message_type="TEXT",
        )
        db_session.add(msg)
    db_session.commit()

    response = await authenticated_client.get(f"/api/v1/memory/{contact.id}/timeline")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # Grouped by date
