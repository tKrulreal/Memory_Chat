"""
Memory Worker — background worker subscribe EventBus → trigger Memory Refresh.

Trigger logic:
- SEND_MESSAGE → check: nếu conversation idle > 5 phút → trigger refresh
- CLOSE_CHAT → trigger refresh ngay
- OPEN_AI (manual button) → trigger refresh ngay
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from src.agents.memory import MemoryAgent
from src.events.bus import EventBus
from src.events.types import ChatEvent, EventType
from src.models.contact import ContactMemory
from src.models.chat import Conversation, Message
from src.services.vector_store import VectorStoreService

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Configurable idle threshold (minutes)
MEMORY_IDLE_THRESHOLD_MINUTES = 5


class MemoryWorker:
    """
    Background worker xử lý memory refresh dựa trên events từ EventBus.
    """

    def __init__(
        self,
        event_bus: EventBus,
        session_factory,
    ):
        self._event_bus = event_bus
        self._session_factory = session_factory
        # Lazy-init MemoryAgent — tránh crash khi thiếu OpenAI key khi worker khởi động
        self._agent: MemoryAgent | None = None
        self._vector_store = VectorStoreService.get_instance()
        self._pending_contacts: set[uuid.UUID] = set()
        self._lock = asyncio.Lock()

    def _get_agent(self) -> MemoryAgent:
        """Lazy khởi tạo MemoryAgent (chỉ tạo khi thực sự cần)."""
        if self._agent is None:
            self._agent = MemoryAgent()
        return self._agent

    def subscribe(self) -> None:
        """Đăng ký handlers với EventBus."""
        self._event_bus.subscribe(EventType.SEND_MESSAGE, self._on_send_message)
        self._event_bus.subscribe(EventType.CLOSE_CHAT, self._on_close_chat)
        self._event_bus.subscribe(EventType.OPEN_AI, self._on_open_ai)
        logger.info("MemoryWorker subscribed to EventBus events")

    async def _on_send_message(self, event: ChatEvent) -> None:
        """Handler cho SEND_MESSAGE — check idle và trigger nếu cần."""
        conversation_id = event.conversation_id
        if not conversation_id:
            return

        # Check conversation idle time
        session = self._session_factory()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conversation:
                return

            # Nếu last_message_time là None hoặc quá threshold → trigger
            should_trigger = False
            if conversation.last_message_time is None:
                should_trigger = True
            else:
                now = datetime.now(timezone.utc)
                last_time = conversation.last_message_time
                if last_time.tzinfo is None:
                    last_time = last_time.replace(tzinfo=timezone.utc)
                idle_minutes = (now - last_time).total_seconds() / 60
                should_trigger = idle_minutes >= MEMORY_IDLE_THRESHOLD_MINUTES

            if should_trigger:
                logger.info(
                    "SEND_MESSAGE: triggering memory refresh for contact_id=%s (idle detected)",
                    conversation.contact_id,
                )
                await self._queue_refresh(conversation.contact_id)
        finally:
            session.close()

    async def _on_close_chat(self, event: ChatEvent) -> None:
        """Handler cho CLOSE_CHAT — trigger refresh ngay."""
        conversation_id = event.conversation_id
        if not conversation_id:
            return

        session = self._session_factory()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            if conversation:
                logger.info(
                    "CLOSE_CHAT: triggering memory refresh for contact_id=%s",
                    conversation.contact_id,
                )
                await self._queue_refresh(conversation.contact_id)
        finally:
            session.close()

    async def _on_open_ai(self, event: ChatEvent) -> None:
        """Handler cho OPEN_AI (manual button) — trigger refresh ngay."""
        contact_id = event.payload.get("contact_id")
        if contact_id:
            try:
                cid = uuid.UUID(str(contact_id))
                logger.info(
                    "OPEN_AI: triggering memory refresh for contact_id=%s (manual)",
                    cid,
                )
                await self._queue_refresh(cid)
            except Exception as e:
                logger.warning("OPEN_AI: invalid contact_id=%s: %s", contact_id, e)

    async def _queue_refresh(self, contact_id: uuid.UUID) -> None:
        """Queue contact để refresh (tránh duplicate)."""
        async with self._lock:
            if contact_id in self._pending_contacts:
                logger.debug("Contact %s already pending refresh, skipping", contact_id)
                return
            self._pending_contacts.add(contact_id)

        # Run refresh async
        asyncio.create_task(self._refresh_contact(contact_id))

    async def _refresh_contact(self, contact_id: uuid.UUID) -> None:
        """Refresh memory cho một contact."""
        try:
            await self._do_refresh(contact_id)
        except Exception as e:
            logger.exception("Memory refresh failed for contact_id=%s: %s", contact_id, e)
            # Retry once after 30 seconds
            await asyncio.sleep(30)
            try:
                await self._do_refresh(contact_id)
                logger.info("Memory refresh RETRY succeeded for contact_id=%s", contact_id)
            except Exception as retry_e:
                logger.exception("Memory refresh RETRY failed for contact_id=%s: %s", contact_id, retry_e)
        finally:
            async with self._lock:
                self._pending_contacts.discard(contact_id)

    async def _do_refresh(self, contact_id: uuid.UUID) -> None:
        """Thực hiện refresh memory."""
        logger.info("Memory refresh started for contact_id=%s", contact_id)

        session = self._session_factory()
        try:
            # Lấy messages (last 100, oldest first)
            messages = (
                session.query(Message)
                .join(Conversation, Conversation.id == Message.conversation_id)
                .filter(Conversation.contact_id == contact_id)
                .order_by(Message.created_at.desc())
                .limit(100)
                .all()
            )

            if not messages:
                logger.info("No messages found for contact_id=%s, skipping", contact_id)
                return

            # Convert to dict (oldest first)
            messages_data = [
                {
                    "content": msg.content,
                    "sender_type": msg.sender_type,
                    "created_at": msg.created_at,
                }
                for msg in reversed(messages)
            ]

            # Build memory (lazy-init agent)
            agent = self._get_agent()
            result = await agent.build_memory(contact_id, messages_data)

            # Lưu vào DB
            memory_dict = result.to_contact_memory_dict(contact_id)

            # Upsert ContactMemory
            existing = session.query(ContactMemory).filter(
                ContactMemory.contact_id == contact_id
            ).first()

            if existing:
                for key, value in memory_dict.items():
                    if key != "contact_id":
                        setattr(existing, key, value)
                logger.info("Updated ContactMemory for contact_id=%s", contact_id)
            else:
                new_memory = ContactMemory(**memory_dict)
                session.add(new_memory)
                logger.info("Created ContactMemory for contact_id=%s", contact_id)

            session.commit()

            # Upsert vào ChromaDB — dùng cùng LLM instance từ MemoryAgent
            memory_id = str(existing.id) if existing else str(uuid.uuid4())
            text_for_embedding = (
                f"Summary: {result.summary}\n"
                f"Company: {result.company or 'N/A'}\n"
                f"Profession: {result.profession or 'N/A'}\n"
                f"Skills: {', '.join(result.skills)}\n"
                f"Interests: {', '.join(result.interests)}\n"
            )

            try:
                # Reuse LLM from MemoryAgent thay vì tạo instance mới
                embedding = agent._llm.embed(text_for_embedding)

                self._vector_store.upsert(
                    memory_id=memory_id,
                    text=text_for_embedding,
                    embedding=embedding,
                    metadata={
                        "contact_id": str(contact_id),
                        "relationship_score": result.relationship_score,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    },
                )
                logger.info("Upserted memory to ChromaDB for contact_id=%s", contact_id)
            except Exception as emb_e:
                logger.warning("Failed to embed memory for contact_id=%s: %s", contact_id, emb_e)

        finally:
            session.close()
