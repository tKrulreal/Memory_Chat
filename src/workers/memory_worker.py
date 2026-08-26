"""
Memory Worker — background worker subscribe EventBus (via Outbox) → trigger Memory Refresh.

Trigger logic:
- NEW_MESSAGE → check: nếu conversation idle > 5 phút → trigger refresh cho CẢ 2 user
- CLOSE_CHAT → trigger refresh ngay cho CẢ 2 user
- OPEN_AI (manual) → trigger refresh ngay cho 1 user cụ thể
"""

import asyncio
import logging
import uuid
from datetime import UTC, datetime

from src.agents.memory import MemoryAgent
from src.events.bus import EventBus
from src.events.types import ChatEvent, EventType
from src.models.ai import AssistantMemory
from src.models.chat import Conversation, Message
from src.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

# Configurable idle threshold (minutes)
MEMORY_IDLE_THRESHOLD_MINUTES = 5


class MemoryWorker:
    """
    Background worker xử lý memory refresh dựa trên events.
    """

    def __init__(
        self,
        event_bus: EventBus,
        session_factory,
    ):
        self._event_bus = event_bus
        self._session_factory = session_factory
        self._agent: MemoryAgent | None = None
        self._vector_store = VectorStoreService.get_instance()
        self._pending_tasks: set[tuple[uuid.UUID, uuid.UUID]] = set() # (user_id, conversation_id)
        self._lock = asyncio.Lock()

    def _get_agent(self) -> MemoryAgent:
        if self._agent is None:
            self._agent = MemoryAgent()
        return self._agent

    def subscribe(self) -> None:
        self._event_bus.subscribe(EventType.NEW_MESSAGE, self._on_send_message)
        self._event_bus.subscribe(EventType.CLOSE_CHAT, self._on_close_chat)
        self._event_bus.subscribe(EventType.OPEN_AI, self._on_open_ai)
        logger.info("MemoryWorker subscribed to EventBus events")

    async def _check_and_queue_refresh(self, session, user_id: uuid.UUID, conversation_id: uuid.UUID, trigger_reason: str):
        from src.models.user import User
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return
            
        setting = user.setting
        
        # Check global toggle
        if not setting or not setting.ai_enabled:
            logger.info("MemoryWorker: AI is globally disabled for user_id=%s. Skipping memory refresh.", user_id)
            return

        # Check chat extraction toggle
        if setting and getattr(setting, "ai_extract_chat", True) is False:
            logger.info("MemoryWorker: AI chat extraction is disabled for user_id=%s. Skipping memory refresh.", user_id)
            return

        # Check specific memory toggle
        from src.models.tag import AISystemConfig
        ai_config = session.query(AISystemConfig).filter(
            AISystemConfig.user_id == user_id,
            AISystemConfig.key == "ai_settings"
        ).first()
        
        if ai_config and isinstance(ai_config.value, dict):
            features = ai_config.value.get("features", {})
            if features.get("memory") is False:
                logger.info("MemoryWorker: AI Memory feature is disabled for user_id=%s. Skipping memory refresh.", user_id)
                return

        interval_str = getattr(setting, "ai_memory_refresh_interval", "realtime") if setting else "realtime"
        
        if interval_str == "daily":
            threshold_minutes = 1440
        elif interval_str == "5_mins":
            threshold_minutes = 5
        else:
            threshold_minutes = 0 # realtime

        memory = session.query(AssistantMemory).filter(
            AssistantMemory.conversation_id == conversation_id,
            AssistantMemory.owner_user_id == user_id
        ).first()

        should_trigger = False
        if not memory:
            should_trigger = True
        else:
            now = datetime.now(UTC)
            last_time = memory.updated_at
            if last_time.tzinfo is None:
                last_time = last_time.replace(tzinfo=UTC)
            idle_minutes = (now - last_time).total_seconds() / 60
            should_trigger = idle_minutes >= threshold_minutes

        if should_trigger:
            logger.info(
                "%s: triggering memory refresh for user_id=%s in conv=%s (idle threshold=%s mins)",
                trigger_reason, user_id, conversation_id, threshold_minutes
            )
            await self._queue_refresh(user_id, conversation_id)

    async def _on_send_message(self, event: ChatEvent) -> None:
        conversation_id = event.conversation_id
        if not conversation_id:
            return

        session = self._session_factory()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conversation:
                return

            await self._check_and_queue_refresh(session, conversation.user_a_id, conversation_id, "NEW_MESSAGE")
            await self._check_and_queue_refresh(session, conversation.user_b_id, conversation_id, "NEW_MESSAGE")
        finally:
            session.close()

    async def _on_close_chat(self, event: ChatEvent) -> None:
        conversation_id = event.conversation_id
        if not conversation_id:
            return

        session = self._session_factory()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            if conversation:
                await self._check_and_queue_refresh(session, conversation.user_a_id, conversation_id, "CLOSE_CHAT")
                await self._check_and_queue_refresh(session, conversation.user_b_id, conversation_id, "CLOSE_CHAT")
        finally:
            session.close()

    async def _on_open_ai(self, event: ChatEvent) -> None:
        conversation_id = event.conversation_id
        user_id = event.user_id
        if conversation_id and user_id:
            logger.info(
                "OPEN_AI: triggering memory refresh for conversation_id=%s, user_id=%s (manual)",
                conversation_id, user_id
            )
            await self._queue_refresh(user_id, conversation_id)

    async def _queue_refresh(self, user_id: uuid.UUID, conversation_id: uuid.UUID) -> None:
        task_key = (user_id, conversation_id)
        async with self._lock:
            if task_key in self._pending_tasks:
                return
            self._pending_tasks.add(task_key)

        asyncio.create_task(self._refresh_memory(user_id, conversation_id))

    async def _refresh_memory(self, user_id: uuid.UUID, conversation_id: uuid.UUID) -> None:
        from src.core.metrics import ai_job_failures_total, ai_job_duration_seconds
        
        task_key = (user_id, conversation_id)
        try:
            with ai_job_duration_seconds.labels(worker_type="memory_worker").time():
                await self._do_refresh(user_id, conversation_id)
        except Exception as e:
            logger.exception("Memory refresh failed for %s: %s", task_key, e)
            ai_job_failures_total.labels(worker_type="memory_worker").inc()
            await asyncio.sleep(30)
            try:
                with ai_job_duration_seconds.labels(worker_type="memory_worker_retry").time():
                    await self._do_refresh(user_id, conversation_id)
            except Exception as retry_e:
                logger.exception("Memory refresh RETRY failed for %s: %s", task_key, retry_e)
                ai_job_failures_total.labels(worker_type="memory_worker_retry").inc()
        finally:
            async with self._lock:
                self._pending_tasks.discard(task_key)

    async def _do_refresh(self, user_id: uuid.UUID, conversation_id: uuid.UUID) -> None:
        logger.info("Memory refresh started for user_id=%s, conv_id=%s", user_id, conversation_id)

        session = self._session_factory()
        try:
            messages = (
                session.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(100)
                .all()
            )

            if not messages:
                return

            messages_data = [
                {
                    "content": msg.content,
                    "sender_user_id": str(msg.sender_user_id),
                    "created_at": msg.created_at,
                }
                for msg in reversed(messages)
            ]

            agent = self._get_agent()
            result = await agent.build_memory(user_id, conversation_id, messages_data, db=session)

            existing = session.query(AssistantMemory).filter(
                AssistantMemory.owner_user_id == user_id,
                AssistantMemory.conversation_id == conversation_id
            ).with_for_update().first()

            if existing:
                existing.summary = result.summary
                existing.facts = result.facts
                existing.through_message_id = str(messages[0].id)
                logger.info("Updated AssistantMemory for user_id=%s", user_id)
            else:
                new_memory = AssistantMemory(
                    owner_user_id=user_id,
                    conversation_id=conversation_id,
                    summary=result.summary,
                    facts=result.facts,
                    through_message_id=str(messages[0].id)
                )
                session.add(new_memory)
                existing = new_memory
                logger.info("Created AssistantMemory for user_id=%s", user_id)

            # Publish MEMORY_UPDATED event within the same transaction
            self._event_bus.publish(
                db=session,
                event_type=EventType.MEMORY_UPDATED,
                user_id=user_id,
                payload={},
                conversation_id=conversation_id,
            )

            session.commit()

            memory_id = str(existing.id)
            
            # Create a rich text for embedding
            facts_str = "\n".join([f"- {k}: {v}" for k, v in (result.facts or {}).items()])
            text_for_embedding = f"Summary: {result.summary}\nFacts:\n{facts_str}"

            try:
                embedding = agent._llm.embed(text_for_embedding)

                self._vector_store.upsert(
                    memory_id=memory_id,
                    text=text_for_embedding,
                    embedding=embedding,
                    metadata={
                        "owner_user_id": str(user_id),
                        "conversation_id": str(conversation_id),
                        "updated_at": datetime.now(UTC).isoformat(),
                    },
                )
                logger.info("Upserted memory to Qdrant for user_id=%s", user_id)
            except Exception as emb_e:
                logger.warning("Failed to embed memory for user_id=%s: %s", user_id, emb_e)

        finally:
            session.close()
