import logging
import uuid
from typing import Any, TypedDict

import chromadb
from chromadb.config import Settings as ChromaSettings

from src.config import get_settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "contact_memory_embedding"


class VectorSearchResult(TypedDict):
    ids: list[str]
    embeddings: list[list[float]]
    documents: list[str]
    metadatas: list[dict[str, Any]]


class VectorStoreService:
    """Wrapper cho ChromaDB — quản lý collection contact_memory_embedding."""

    _instance: "VectorStoreService | None" = None

    def __init__(self):
        settings = get_settings()
        self.persist_dir = settings.chroma_persist_dir
        self._client: chromadb.PersistentClient | None = None
        self._collection: chromadb.Collection | None = None

    @classmethod
    def get_instance(cls) -> "VectorStoreService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get_client(self) -> chromadb.PersistentClient:
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        return self._client

    def _get_collection(self) -> chromadb.Collection:
        if self._collection is None:
            client = self._get_client()
            try:
                self._collection = client.get_collection(name=COLLECTION_NAME)
                logger.info("Connected to existing collection '%s'", COLLECTION_NAME)
            except Exception:
                self._collection = client.create_collection(
                    name=COLLECTION_NAME,
                    metadata={"description": "Contact memory embeddings for semantic search"},
                )
                logger.info("Created new collection '%s'", COLLECTION_NAME)
        return self._collection

    def upsert(
        self,
        memory_id: str,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Lưu hoặc cập nhật một embedding vào collection.

        Args:
            memory_id: Unique ID cho memory (dùng làm document ID)
            text: Nội dung text gốc
            embedding: Vector 1536 dim
            metadata: Metadata kèm theo (contact_id, user_id, updated_at...)
        """
        # ChromaDB requires non-empty metadata
        if not metadata:
            metadata = {"memory_id": str(memory_id)}
        collection = self._get_collection()
        collection.upsert(
            ids=[str(memory_id)],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
        )
        logger.info("Upserted memory_id=%s into collection", memory_id)

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        where: dict[str, Any] | None = None,
    ) -> VectorSearchResult:
        """
        Tìm top-k embeddings gần nhất.

        Args:
            query_embedding: Vector query
            top_k: Số lượng kết quả trả về
            where: Filter metadata (e.g. {"contact_id": "uuid-string"})

        Returns:
            Dict với keys: ids, embeddings, documents, metadatas
        """
        collection = self._get_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "embeddings", "metadatas"],
        )

        # Normalize output shape
        return VectorSearchResult(
            ids=results["ids"][0] if results["ids"] else [],
            embeddings=results["embeddings"][0] if results["embeddings"] else [],
            documents=results["documents"][0] if results["documents"] else [],
            metadatas=results["metadatas"][0] if results["metadatas"] else [],
        )

    def delete(self, memory_id: str) -> None:
        """Xoá một memory khỏi collection."""
        collection = self._get_collection()
        collection.delete(ids=[str(memory_id)])
        logger.info("Deleted memory_id=%s from collection", memory_id)

    def count(self) -> int:
        """Đếm số lượng embeddings trong collection."""
        collection = self._get_collection()
        return collection.count()

    def get_by_contact(self, contact_id: str, top_k: int = 10) -> VectorSearchResult:
        """
        Lấy tất cả embeddings của một contact, sắp xếp theo updated_at DESC.

        Args:
            contact_id: UUID string của contact
            top_k: Giới hạn số lượng

        Returns:
            List các memory của contact đó
        """
        return self.query(
            query_embedding=[0.0] * 1536,  # Dummy vector — not used for filtering
            top_k=top_k,
            where={"contact_id": str(contact_id)},
        )

    def reset(self) -> None:
        """Xoá toàn bộ collection (dùng cho testing)."""
        client = self._get_client()
        try:
            client.delete_collection(name=COLLECTION_NAME)
            logger.warning("Deleted collection '%s'", COLLECTION_NAME)
        except Exception:
            pass
        self._collection = None

    def close(self) -> None:
        """
        Đóng persistent client và giải phóng file handles.

        Quan trọng cho Windows testing — tránh PermissionError khi xóa tempdir.
        """
        # Reset singleton reference first
        VectorStoreService._instance = None
        # Try close() on client to release native handles
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
        self._collection = None
        self._client = None
