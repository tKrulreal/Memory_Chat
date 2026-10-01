import uuid
import pytest
from src.models.user import User, UserProfile


@pytest.mark.asyncio
async def test_get_and_update_my_profile(authenticated_client):
    # 1. Get initial profile
    get_res = await authenticated_client.get("/api/v1/profile/me")
    assert get_res.status_code == 200
    data = get_res.json()
    assert "email" in data
    assert "skills" in data
    assert "interests" in data
    assert data["is_public"] is True

    # 2. Update profile with custom fields including is_public, social links, experience
    payload = {
        "full_name": "Test User Updated",
        "profession": "Staff AI Engineer",
        "company": "NextGen AI Labs",
        "location": "Hà Nội",
        "is_public": True,
        "github": "https://github.com/testuser",
        "linkedin": "https://linkedin.com/in/testuser",
        "website": "https://testuser.dev",
        "skills": ["Python", "PyTorch", "LLM", "RAG"],
        "interests": ["Generative AI", "Startups"],
        "looking_for": ["Tìm Senior Mobile Developer"],
        "offering": ["Tư vấn kiến trúc AI RAG"],
        "bio": "Đam mê xây dựng các hệ thống AI ứng dụng thực tế.",
        "experience": [
            {"title": "Staff AI Engineer", "company": "NextGen AI Labs", "period": "2023 - Nay"}
        ],
        "education": [
            {"school": "Đại học Bách Khoa", "degree": "Kỹ sư CNTT", "year": "2021"}
        ],
    }

    put_res = await authenticated_client.put("/api/v1/profile/me", json=payload)
    assert put_res.status_code == 200
    updated_data = put_res.json()

    assert updated_data["full_name"] == "Test User Updated"
    assert updated_data["profession"] == "Staff AI Engineer"
    assert updated_data["company"] == "NextGen AI Labs"
    assert updated_data["location"] == "Hà Nội"
    assert updated_data["is_public"] is True
    assert updated_data["github"] == "https://github.com/testuser"
    assert "Python" in updated_data["skills"]
    assert "Startups" in updated_data["interests"]
    assert "Tìm Senior Mobile Developer" in updated_data["looking_for"]
    assert "Tư vấn kiến trúc AI RAG" in updated_data["offering"]
    assert len(updated_data["experience"]) == 1
    assert len(updated_data["education"]) == 1
    assert updated_data["is_custom_profile"] is True

    # 3. Read back to confirm persistence in DB
    get_res_again = await authenticated_client.get("/api/v1/profile/me")
    assert get_res_again.status_code == 200
    persisted_data = get_res_again.json()
    assert persisted_data["profession"] == "Staff AI Engineer"
    assert persisted_data["location"] == "Hà Nội"
    assert persisted_data["is_public"] is True
    assert persisted_data["is_custom_profile"] is True


@pytest.mark.asyncio
async def test_get_target_user_public_and_private_profile(authenticated_client, db_session):
    # Create target user with public profile
    target_public = User(
        id=uuid.uuid4(),
        email="target.public@example.com",
        password_hash="hash",
        full_name="Target Public User",
    )
    db_session.add(target_public)
    db_session.commit()

    prof_public = UserProfile(
        user_id=target_public.id,
        profession="DevOps Lead",
        company="CloudTech",
        is_public=True,
        skills=["Kubernetes", "Docker", "AWS"],
        bio="Chuyên gia Cloud.",
    )
    db_session.add(prof_public)
    db_session.commit()

    # Query public profile
    res_pub = await authenticated_client.get(f"/api/v1/profile/{target_public.id}")
    assert res_pub.status_code == 200
    pub_data = res_pub.json()
    assert pub_data["full_name"] == "Target Public User"
    assert pub_data["profession"] == "DevOps Lead"
    assert pub_data["is_public"] is True
    assert "Kubernetes" in pub_data["skills"]
    assert pub_data["connection_status"] == "NONE"

    # Create target user with PRIVATE profile (is_public=False)
    target_private = User(
        id=uuid.uuid4(),
        email="target.private@example.com",
        password_hash="hash",
        full_name="Target Private User",
    )
    db_session.add(target_private)
    db_session.commit()

    prof_private = UserProfile(
        user_id=target_private.id,
        profession="Security Researcher",
        company="SecretLab",
        is_public=False,
        skills=["Exploit", "Reverse Engineering"],
        bio="Thông tin mật.",
    )
    db_session.add(prof_private)
    db_session.commit()

    # Query private profile (stranger -> limited view)
    res_priv = await authenticated_client.get(f"/api/v1/profile/{target_private.id}")
    assert res_priv.status_code == 200
    priv_data = res_priv.json()
    assert priv_data["is_public"] is False
    assert priv_data["skills"] == []
    assert "riêng tư" in priv_data["bio"]
