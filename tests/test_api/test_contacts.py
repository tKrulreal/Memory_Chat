import uuid

import pytest

from src.models.contact import Contact


@pytest.mark.asyncio
async def test_contact_crud(authenticated_client):
    created = await authenticated_client.post(
        "/api/v1/contacts",
        json={
            "name": "Alice",
            "avatar_url": "https://example.com/alice.png",
            "relationship_score": 8,
        },
    )

    assert created.status_code == 201
    contact = created.json()
    assert contact["name"] == "Alice"
    assert contact["avatar_url"] == "https://example.com/alice.png"
    assert contact["relationship_score"] == 8

    detail = await authenticated_client.get(f"/api/v1/contacts/{contact['id']}")
    assert detail.status_code == 200
    assert detail.json()["id"] == contact["id"]

    updated = await authenticated_client.put(
        f"/api/v1/contacts/{contact['id']}",
        json={"name": "Alice Updated", "relationship_score": 9},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Alice Updated"
    assert updated.json()["relationship_score"] == 9

    deleted = await authenticated_client.delete(f"/api/v1/contacts/{contact['id']}")
    assert deleted.status_code == 204

    missing = await authenticated_client.get(f"/api/v1/contacts/{contact['id']}")
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_contact_list_filters_paginates_and_excludes_other_users(
    authenticated_client, db_session, current_user, other_user
):
    db_session.add_all(
        [
            Contact(user_id=current_user.id, display_name="Alice"),
            Contact(user_id=current_user.id, display_name="Bob"),
            Contact(user_id=current_user.id, display_name="Bobby"),
            Contact(user_id=other_user.id, display_name="Private Bob"),
        ]
    )
    db_session.commit()

    response = await authenticated_client.get("/api/v1/contacts", params={"search": "bob", "limit": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"] == {"page": 1, "limit": 1, "total": 2}
    assert [contact["name"] for contact in body["data"]] == ["Bob"]


@pytest.mark.asyncio
async def test_contact_returns_403_for_foreign_owner(authenticated_client, db_session, other_user):
    foreign_contact = Contact(user_id=other_user.id, display_name="Private")
    db_session.add(foreign_contact)
    db_session.commit()

    response = await authenticated_client.get(f"/api/v1/contacts/{foreign_contact.id}")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_contact_requires_authentication(client):
    response = await client.get("/api/v1/contacts")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_contact_rejects_invalid_identifiers_and_pagination(authenticated_client):
    invalid_id = await authenticated_client.get(f"/api/v1/contacts/{uuid.uuid4()}-bad")
    invalid_page = await authenticated_client.get("/api/v1/contacts", params={"page": 0})

    assert invalid_id.status_code == 422
    assert invalid_page.status_code == 422
