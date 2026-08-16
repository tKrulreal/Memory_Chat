import pytest


@pytest.mark.asyncio
async def test_get_and_update_my_profile(authenticated_client):
    # 1. Get initial profile
    get_res = await authenticated_client.get("/api/v1/profile/me")
    assert get_res.status_code == 200
    data = get_res.json()
    assert "email" in data
    assert "skills" in data
    assert "interests" in data

    # 2. Update profile with custom fields
    payload = {
        "full_name": "Test User Updated",
        "profession": "Staff AI Engineer",
        "company": "NextGen AI Labs",
        "location": "Hà Nội",
        "skills": ["Python", "PyTorch", "LLM", "RAG"],
        "interests": ["Generative AI", "Startups"],
        "looking_for": ["Tìm Senior Mobile Developer"],
        "offering": ["Tư vấn kiến trúc AI RAG"],
        "bio": "Đam mê xây dựng các hệ thống AI ứng dụng thực tế.",
    }

    put_res = await authenticated_client.put("/api/v1/profile/me", json=payload)
    assert put_res.status_code == 200
    updated_data = put_res.json()

    assert updated_data["full_name"] == "Test User Updated"
    assert updated_data["profession"] == "Staff AI Engineer"
    assert updated_data["company"] == "NextGen AI Labs"
    assert updated_data["location"] == "Hà Nội"
    assert "Python" in updated_data["skills"]
    assert "Startups" in updated_data["interests"]
    assert "Tìm Senior Mobile Developer" in updated_data["looking_for"]
    assert "Tư vấn kiến trúc AI RAG" in updated_data["offering"]
    assert updated_data["is_custom_profile"] is True

    # 3. Read back to confirm persistence in DB
    get_res_again = await authenticated_client.get("/api/v1/profile/me")
    assert get_res_again.status_code == 200
    persisted_data = get_res_again.json()
    assert persisted_data["profession"] == "Staff AI Engineer"
    assert persisted_data["location"] == "Hà Nội"
    assert persisted_data["is_custom_profile"] is True
