"""
Tests cho VectorStoreService (ChromaDB wrapper).
"""

import tempfile
import uuid
from unittest.mock import patch

import pytest

from src.services.vector_store import VectorStoreService


@pytest.fixture
def vector_store():
    """Tạo VectorStoreService với thư mục tạm."""
    # Reset singleton before each test
    VectorStoreService._instance = None
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("src.services.vector_store.get_settings") as mock_settings:
            mock_settings.return_value.chroma_persist_dir = tmpdir
            vs = VectorStoreService()
            VectorStoreService._instance = vs  # Set singleton
            yield vs
            # Close client + reset singleton trước khi xóa tempdir
            # Tránh PermissionError trên Windows do file handles
            try:
                vs.close()
            except Exception:
                pass
            VectorStoreService._instance = None


class TestVectorStoreService:
    def test_upsert_and_query(self, vector_store):
        memory_id = str(uuid.uuid4())
        embedding = [0.1] * 1536
        metadata = {
            "contact_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "updated_at": "2026-08-03T10:00:00Z",
        }

        vector_store.upsert(memory_id, "Người này thích lập trình Python", embedding, metadata)

        results = vector_store.query(embedding, top_k=5)

        assert results["ids"] == [memory_id]
        assert results["documents"] == ["Người này thích lập trình Python"]
        assert results["metadatas"][0]["contact_id"] == metadata["contact_id"]

    def test_count(self, vector_store):
        assert vector_store.count() == 0

        for i in range(3):
            vector_store.upsert(
                str(uuid.uuid4()),
                f"Text {i}",
                [0.1] * 1536,
                {"contact_id": str(uuid.uuid4())},
            )

        assert vector_store.count() == 3

    def test_delete(self, vector_store):
        memory_id = str(uuid.uuid4())
        vector_store.upsert(memory_id, "Test delete", [0.1] * 1536, {"v": 1})

        assert vector_store.count() == 1
        vector_store.delete(memory_id)
        assert vector_store.count() == 0

    def test_query_with_filter(self, vector_store):
        contact_id = str(uuid.uuid4())
        for i in range(3):
            vector_store.upsert(
                str(uuid.uuid4()),
                f"Text contact {i}",
                [0.1] * 1536,
                {"contact_id": contact_id},
            )
        other_id = str(uuid.uuid4())
        vector_store.upsert(
            str(uuid.uuid4()),
            "Text other contact",
            [0.1] * 1536,
            {"contact_id": other_id},
        )

        results = vector_store.query(
            [0.1] * 1536,
            top_k=10,
            where={"contact_id": contact_id},
        )

        assert len(results["ids"]) == 3
        for meta in results["metadatas"]:
            assert meta["contact_id"] == contact_id

    def test_upsert_updates_existing(self, vector_store):
        memory_id = str(uuid.uuid4())
        vector_store.upsert(memory_id, "Original", [0.1] * 1536, {"v": 1})
        vector_store.upsert(memory_id, "Updated", [0.2] * 1536, {"v": 2})

        results = vector_store.query([0.1] * 1536, top_k=10)
        # Should have only 1 entry (updated)
        assert len(results["ids"]) == 1
        assert results["documents"] == ["Updated"]

    def test_get_by_contact(self, vector_store):
        contact_id = str(uuid.uuid4())
        for i in range(3):
            vector_store.upsert(
                str(uuid.uuid4()),
                f"Memory {i}",
                [0.1] * 1536,
                {"contact_id": contact_id},
            )

        results = vector_store.get_by_contact(contact_id, top_k=5)
        assert len(results["ids"]) == 3
