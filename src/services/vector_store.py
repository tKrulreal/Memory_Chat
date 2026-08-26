import logging
from typing import Any, TypedDict
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue, PointStruct

from src.config import get_settings

logger = logging.getLogger(__name__)


class VectorSearchResult(TypedDict):
    ids: list[str]
    embeddings: list[list[float]]
    documents: list[str]
    metadatas: list[dict[str, Any]]


class VectorStoreService:
    """
    Wrapper cho Qdrant Cloud — quản lý embeddings cho AssistantMemory.

    Collection name được đọc từ settings.qdrant_collection (mặc định: "assistant_memories").
    Mỗi vector bắt buộc có payload.owner_user_id để đảm bảo ACL — không có user nào
    truy cập được memory của user khác qua semantic search.
    """

    _instance: "VectorStoreService | None" = None

    def __init__(self):
        settings = get_settings()
        self.qdrant_url = settings.qdrant_url
        self.qdrant_api_key = settings.qdrant_api_key
        self.collection_name = settings.qdrant_collection
        self.profile_collection_name = getattr(settings, "qdrant_profile_collection", "user_profiles")
        self._client: QdrantClient | None = None
        self._initialized = False
        self._profile_initialized = False

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

            if self.collection_name not in collection_names:
                client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                )
                logger.info("Created new Qdrant collection '%s'", self.collection_name)

                # Indexes để filter theo owner (ACL) và conversation
                client.create_payload_index(self.collection_name, field_name="owner_user_id", field_schema="keyword")
                client.create_payload_index(self.collection_name, field_name="conversation_id", field_schema="keyword")
                client.create_payload_index(self.collection_name, field_name="memory_id", field_schema="keyword")
            else:
                logger.info("Connected to existing Qdrant collection '%s'", self.collection_name)

            self._initialized = True
        except Exception as e:
            logger.error("Failed to initialize Qdrant collection '%s': %s", self.collection_name, e)
            raise e

    def upsert(
        self,
        memory_id: str,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Lưu hoặc cập nhật một embedding vào Qdrant Cloud.

        Args:
            memory_id: UUID của AssistantMemory (dùng làm document ID)
            text: Nội dung text gốc để embed
            embedding: Vector 1536 dim từ OpenAI text-embedding-3-small
            metadata: Phải chứa owner_user_id để đảm bảo ACL
        """
        self._ensure_collection()
        client = self._get_client()

        if not metadata:
            metadata = {"memory_id": str(memory_id)}
        else:
            metadata["memory_id"] = str(memory_id)

        # Qdrant tách vector và payload — lưu text gốc vào payload["document"]
        payload = metadata.copy()
        payload["document"] = text

        # Dùng uuid5 để convert memory_id string thành UUID hợp lệ cho Qdrant point ID
        qdrant_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(memory_id)))

        client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=qdrant_id,
                    vector=embedding,
                    payload=payload,
                )
            ],
        )
        logger.info("Upserted memory_id=%s into Qdrant collection '%s'", memory_id, self.collection_name)

    def query(
        self,
        query_embedding: list[float],
        owner_user_id: str,
        conversation_id: str | None = None,
        top_k: int = 10,
        where: dict[str, Any] | None = None,
    ) -> VectorSearchResult:
        """
        Tìm top-k embeddings gần nhất — BẮT BUỘC filter theo owner_user_id (ACL).

        Args:
            query_embedding: Vector query 1536 dim
            owner_user_id: User ID bắt buộc — không search cross-tenant
            conversation_id: Nếu có, giới hạn trong 1 conversation cụ thể
            top_k: Số kết quả trả về
            where: Filter bổ sung theo payload fields
        """
        self._ensure_collection()
        client = self._get_client()

        # owner_user_id là filter bắt buộc — ngăn cross-tenant retrieval
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
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
            with_vectors=True,
        )

        ids_res: list[str] = []
        embeddings_res: list[list[float]] = []
        documents_res: list[str] = []
        metadatas_res: list[dict[str, Any]] = []

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
        """Xóa embedding theo memory_id."""
        self._ensure_collection()
        client = self._get_client()

        client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(key="memory_id", match=MatchValue(value=str(memory_id)))
                ]
            ),
        )
        logger.info("Deleted memory_id=%s from Qdrant collection '%s'", memory_id, self.collection_name)

    def count(self) -> int:
        """Đếm số points trong collection."""
        self._ensure_collection()
        client = self._get_client()
        return client.count(collection_name=self.collection_name).count

    def get_by_conversation(self, owner_user_id: str, conversation_id: str, top_k: int = 10) -> VectorSearchResult:
        """Lấy tất cả memories của một conversation (dùng zero-vector để lấy theo filter)."""
        return self.query(
            query_embedding=[0.0] * 1536,
            owner_user_id=owner_user_id,
            conversation_id=str(conversation_id),
            top_k=top_k,
        )

    def _ensure_profile_collection(self) -> None:
        if self._profile_initialized:
            return

        client = self._get_client()
        try:
            collections = client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.profile_collection_name not in collection_names:
                client.create_collection(
                    collection_name=self.profile_collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                )
                logger.info("Created new Qdrant collection '%s'", self.profile_collection_name)
                client.create_payload_index(self.profile_collection_name, field_name="user_id", field_schema="keyword")
            else:
                logger.info("Connected to existing Qdrant collection '%s'", self.profile_collection_name)

            self._profile_initialized = True
        except Exception as e:
            logger.error("Failed to initialize Qdrant profile collection '%s': %s", self.profile_collection_name, e)
            raise e

    def upsert_profile(
        self,
        user_id: str,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Lưu hoặc cập nhật embedding hồ sơ cá nhân vào Qdrant."""
        self._ensure_profile_collection()
        client = self._get_client()

        payload = (metadata or {}).copy()
        payload["user_id"] = str(user_id)
        payload["document"] = text

        qdrant_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"profile_{user_id}"))

        client.upsert(
            collection_name=self.profile_collection_name,
            points=[
                PointStruct(
                    id=qdrant_id,
                    vector=embedding,
                    payload=payload,
                )
            ],
        )
        logger.info("Upserted user_id=%s profile into Qdrant collection '%s'", user_id, self.profile_collection_name)

    def search_profiles(
        self,
        query_embedding: list[float],
        top_k: int = 50,
        exclude_user_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Tìm kiếm Top-K hồ sơ người dùng tương đồng ngữ nghĩa nhất qua Qdrant.
        Trả về danh sách dict: [{'user_id': ..., 'score': float, 'document': ..., 'metadata': ...}]
        """
        try:
            self._ensure_profile_collection()
            client = self._get_client()

            must_not_conditions = []
            if exclude_user_ids:
                for uid in exclude_user_ids:
                    must_not_conditions.append(
                        FieldCondition(key="user_id", match=MatchValue(value=str(uid)))
                    )

            query_filter = Filter(must_not=must_not_conditions) if must_not_conditions else None

            results = client.search(
                collection_name=self.profile_collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=top_k,
                with_payload=True,
                with_vectors=False,
            )

            candidates = []
            for r in results:
                payload = r.payload or {}
                candidates.append({
                    "user_id": str(payload.get("user_id", "")),
                    "score": float(r.score),
                    "document": payload.get("document", ""),
                    "metadata": {k: v for k, v in payload.items() if k not in ["user_id", "document"]},
                })
            return candidates
        except Exception as e:
            logger.warning("Qdrant search_profiles encountered error or offline: %s", e)
            return []

    def reset(self) -> None:
        """Xoá toàn bộ collection — CHỈ dùng cho testing."""
        client = self._get_client()
        try:
            client.delete_collection(collection_name=self.collection_name)
            logger.warning("Deleted Qdrant collection '%s'", self.collection_name)
        except Exception:
            pass
        try:
            client.delete_collection(collection_name=self.profile_collection_name)
            logger.warning("Deleted Qdrant profile collection '%s'", self.profile_collection_name)
        except Exception:
            pass
        self._initialized = False
        self._profile_initialized = False

    def close(self) -> None:
        """Đóng client và giải phóng resource."""
        VectorStoreService._instance = None
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
        self._client = None
        self._initialized = False
        self._profile_initialized = False
