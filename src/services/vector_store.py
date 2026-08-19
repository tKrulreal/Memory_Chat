import logging
from typing import Any, TypedDict
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue, PointStruct

from src.config import get_settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "contact_memory_embedding"


class VectorSearchResult(TypedDict):
    ids: list[str]
    embeddings: list[list[float]]
    documents: list[str]
    metadatas: list[dict[str, Any]]


class VectorStoreService:
    """Wrapper cho Qdrant — quản lý collection contact_memory_embedding."""

    _instance: "VectorStoreService | None" = None

    def __init__(self):
        settings = get_settings()
        self.qdrant_url = settings.qdrant_url
        self.qdrant_api_key = settings.qdrant_api_key
        self._client: QdrantClient | None = None
        self._initialized = False

    @classmethod
    def get_instance(cls) -> "VectorStoreService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get_client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key if self.qdrant_api_key else None,
            )
        return self._client

    def _ensure_collection(self) -> None:
        if self._initialized:
            return
            
        client = self._get_client()
        try:
            collections = client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if COLLECTION_NAME not in collection_names:
                client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                )
                logger.info("Created new Qdrant collection '%s'", COLLECTION_NAME)
                
                # Create indexes for filtering
                client.create_payload_index(COLLECTION_NAME, field_name="owner_user_id", field_schema="keyword")
                client.create_payload_index(COLLECTION_NAME, field_name="conversation_id", field_schema="keyword")
                client.create_payload_index(COLLECTION_NAME, field_name="memory_id", field_schema="keyword")
            else:
                logger.info("Connected to existing Qdrant collection '%s'", COLLECTION_NAME)
                
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection: {e}")
            raise e

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
        self._ensure_collection()
        client = self._get_client()
        
        if not metadata:
            metadata = {"memory_id": str(memory_id)}
        else:
            # Ensure memory_id is present
            metadata["memory_id"] = str(memory_id)
            
        # Ensure document text is in metadata for Qdrant (since Qdrant separates vector and payload)
        payload = metadata.copy()
        payload["document"] = text
            
        # Use uuid5 to convert memory_id string into a valid UUID for Qdrant
        qdrant_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(memory_id)))
            
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=qdrant_id,
                    vector=embedding,
                    payload=payload
                )
            ]
        )
        logger.info("Upserted memory_id=%s into Qdrant collection", memory_id)

    def query(
        self,
        query_embedding: list[float],
        owner_user_id: str,
        conversation_id: str | None = None,
        top_k: int = 10,
        where: dict[str, Any] | None = None,
    ) -> VectorSearchResult:
        """
        Tìm top-k embeddings gần nhất thuộc về owner_user_id (và conversation_id nếu có).
        """
        self._ensure_collection()
        client = self._get_client()
        
        must_conditions = [
            FieldCondition(key="owner_user_id", match=MatchValue(value=str(owner_user_id)))
        ]
        
        if conversation_id:
            must_conditions.append(
                FieldCondition(key="conversation_id", match=MatchValue(value=str(conversation_id)))
            )
            
        if where:
            for k, v in where.items():
                must_conditions.append(
                    FieldCondition(key=k, match=MatchValue(value=str(v)))
                )
                
        query_filter = Filter(must=must_conditions)

        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
            with_vectors=True,
        )
        
        ids_res = []
        embeddings_res = []
        documents_res = []
        metadatas_res = []
        
        for r in results:
            payload = r.payload or {}
            ids_res.append(str(payload.get("memory_id", r.id)))
            embeddings_res.append(r.vector or [])
            documents_res.append(payload.get("document", ""))
            
            meta = payload.copy()
            meta.pop("document", None)
            metadatas_res.append(meta)

        return VectorSearchResult(
            ids=ids_res,
            embeddings=embeddings_res,
            documents=documents_res,
            metadatas=metadatas_res,
        )

    def delete(self, memory_id: str) -> None:
        self._ensure_collection()
        client = self._get_client()
        
        # Qdrant delete by exact payload match (since we mapped memory_id -> UUID)
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(key="memory_id", match=MatchValue(value=str(memory_id)))
                ]
            )
        )
        logger.info("Deleted memory_id=%s from Qdrant collection", memory_id)

    def count(self) -> int:
        self._ensure_collection()
        client = self._get_client()
        return client.count(collection_name=COLLECTION_NAME).count

    def get_by_conversation(self, owner_user_id: str, conversation_id: str, top_k: int = 10) -> VectorSearchResult:
        return self.query(
            query_embedding=[0.0] * 1536,
            owner_user_id=owner_user_id,
            conversation_id=str(conversation_id),
            top_k=top_k,
        )

    def reset(self) -> None:
        """Xoá toàn bộ collection (dùng cho testing)."""
        client = self._get_client()
        try:
            client.delete_collection(collection_name=COLLECTION_NAME)
            logger.warning("Deleted Qdrant collection '%s'", COLLECTION_NAME)
        except Exception:
            pass
        self._initialized = False

    def close(self) -> None:
        """
        Đóng client và giải phóng resource.
        """
        VectorStoreService._instance = None
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
        self._client = None
        self._initialized = False
