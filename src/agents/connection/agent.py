"""
Connection Agent — đề xuất kết nối giữa 2 Contacts.

Agent này phân tích Memory và Embedding để tìm
các cặp contacts có thể được kết nối.

Ví dụ:
- Hai Founder cùng tuyển AI Engineer
- Hai người cùng làm Computer Vision
- Hai khách hàng có nhu cầu hợp tác
"""

import json
import logging
import uuid

from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.gateways.llm import LLMGateway
from src.models.contact import Contact, ContactMemory
from src.models.database import SessionLocal
from src.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

# Prompt cho Connection Agent
CONNECTION_REASONING_PROMPT = """Bạn là một Connection Agent cho hệ thống nhắn tin MemoryChat.

Nhiệm vụ: Phân tích 2 contacts và quyết định xem họ có nên được kết nối không.

Contact A: {contact_a}
Contact B: {contact_b}

Hãy đánh giá:
1. Họ có cùng lĩnh vực/ngành nghề không?
2. Họ có thể hỗ trợ nhau không?
3. Họ có chung interest/goals không?
4. Việc kết nối có mang lại giá trị không?

Trả về JSON:
{{
    "should_connect": true/false,
    "reason": "Lý do ngắn gọn vì sao nên/không nên kết nối",
    "connection_type": "COLLEAGUE/INVESTOR/FOUNDER/PROFESSIONAL/SOCIAL/OTHER"
}}

Chỉ trả về JSON, không có text khác."""


class ConnectionPair(BaseModel):
    """Một cặp contacts có thể kết nối."""
    contact_a_id: uuid.UUID
    contact_a_name: str
    contact_b_id: uuid.UUID
    contact_b_name: str
    score: float  # 0-100
    reason: str
    connection_type: str  # COLLEAGUE, INVESTOR, FOUNDER, etc.


class ConnectionAgent:
    def __init__(self, llm: LLMGateway | None = None):
        self._llm = llm or LLMGateway()
        self._vector_store = VectorStoreService.get_instance()

    def _build_contact_summary(self, contact: Contact, memory: ContactMemory | None = None) -> str:
        """Build summary string cho contact."""
        parts = [
            f"Name: {contact.display_name}",
        ]

        if memory:
            if memory.profession:
                parts.append(f"Profession: {memory.profession}")
            if memory.company:
                parts.append(f"Company: {memory.company}")
            if memory.summary:
                parts.append(f"Summary: {memory.summary}")

            # Unwrap dict if skills/interest are stored as {"skills": [...]} or {"interests": [...]}
            if memory.skills:
                if isinstance(memory.skills, dict):
                    skills_list = memory.skills.get("skills", [])
                elif isinstance(memory.skills, list):
                    skills_list = memory.skills
                else:
                    skills_list = []
                parts.append(f"Skills: {', '.join(skills_list)}")

            if memory.interest:
                if isinstance(memory.interest, dict):
                    interests_list = memory.interest.get("interests", [])
                elif isinstance(memory.interest, list):
                    interests_list = memory.interest
                else:
                    interests_list = []
                parts.append(f"Interests: {', '.join(interests_list)}")
        else:
            parts.append("No memory available")

        return "\n".join(parts)

    def _get_contact_embedding_similarity(
        self,
        contact_a_id: uuid.UUID,
        contact_b_id: uuid.UUID,
    ) -> float:
        """
        Tính similarity giữa 2 contacts dựa trên embeddings.

        Dùng ChromaDB để query embeddings gần nhất.
        """
        try:
            # Get all embeddings
            results = self._vector_store.query(
                query_embedding=[0.0] * 1536,  # Dummy for filtering
                top_k=100,
            )

            # Filter for our contacts
            a_scores = []
            b_scores = []
            for doc, meta in zip(results["documents"], results["metadatas"]):
                cid = meta.get("contact_id")
                if cid == str(contact_a_id):
                    # Calculate dummy similarity (we can't get actual embedding comparison here)
                    # In production, we'd use actual embedding distance
                    a_scores.append(1.0)
                elif cid == str(contact_b_id):
                    b_scores.append(1.0)

            # If both contacts have embeddings, assume some base similarity
            if a_scores and b_scores:
                return 50.0  # Base score
            return 0.0

        except Exception as e:
            logger.warning(f"Failed to get embedding similarity: {e}")
            return 0.0

    def _generate_connection_reasoning(
        self,
        contact_a: Contact,
        contact_b: Contact,
        memory_a: ContactMemory | None,
        memory_b: ContactMemory | None,
    ) -> tuple[bool, str, str]:
        """
        Dùng LLM để phân tích và sinh reasoning cho connection.

        Returns: (should_connect, reason, connection_type)
        """
        summary_a = self._build_contact_summary(contact_a, memory_a)
        summary_b = self._build_contact_summary(contact_b, memory_b)

        prompt = CONNECTION_REASONING_PROMPT.format(
            contact_a=summary_a,
            contact_b=summary_b,
        )

        try:
            response = self._llm.complete(prompt).strip()

            # Parse JSON
            if response.startswith("```json"):
                response = response.strip("```json").strip("```").strip()
            elif response.startswith("```"):
                response = response.strip("```").strip()

            data = json.loads(response)
            should_connect = data.get("should_connect", False)
            reason = data.get("reason", "Không có lý do cụ thể")
            connection_type = data.get("connection_type", "OTHER")

            return should_connect, reason, connection_type

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse connection reasoning: {e}")
            return False, "Lỗi khi phân tích kết nối", "OTHER"
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return False, "Lỗi khi gọi LLM", "OTHER"

    async def find_connections(
        self,
        user_id: uuid.UUID,
        db: Session | None = None,
        top_k: int = 5,
    ) -> list[ConnectionPair]:
        """
        Tìm các cặp contacts có thể kết nối cho user.

        Algorithm:
        1. Lấy tất cả contacts của user
        2. Với mỗi cặp, dùng LLM để phân tích
        3. Trả về top-k pairs có score cao nhất

        Args:
            user_id: UUID của user
            db: Database session (optional)
            top_k: Số cặp tối đa trả về

        Returns:
            List of ConnectionPair
        """

        is_local_db = db is None
        db = db or SessionLocal()

        try:
            # Get all contacts with memory for this user
            contacts = db.query(Contact).filter(Contact.user_id == user_id).all()

            if len(contacts) < 2:
                logger.info("Not enough contacts for connection suggestions")
                return []

            # Build contact -> memory mapping
            memories = {
                c.id: db.query(ContactMemory).filter(ContactMemory.contact_id == c.id).first()
                for c in contacts
            }

            # Generate pairs and score them
            pairs: list[ConnectionPair] = []
            checked_pairs: set[tuple] = set()

            for i, contact_a in enumerate(contacts):
                for contact_b in contacts[i + 1:]:
                    # Skip if already checked
                    pair_key = (contact_a.id, contact_b.id)
                    if pair_key in checked_pairs:
                        continue
                    checked_pairs.add(pair_key)

                    # Get LLM reasoning
                    should_connect, reason, conn_type = self._generate_connection_reasoning(
                        contact_a,
                        contact_b,
                        memories.get(contact_a.id),
                        memories.get(contact_b.id),
                    )

                    if should_connect:
                        # Calculate base score from LLM reasoning
                        score = 70.0 if should_connect else 0.0

                        # Boost score if both have memory
                        if memories.get(contact_a.id) and memories.get(contact_b.id):
                            score += 15.0

                        # Boost if shared skills/interests
                        mem_a = memories.get(contact_a.id)
                        mem_b = memories.get(contact_b.id)
                        if mem_a and mem_b:
                            shared = self._count_shared_items(mem_a, mem_b)
                            score += min(shared * 5, 15.0)  # Max +15

                        pair = ConnectionPair(
                            contact_a_id=contact_a.id,
                            contact_a_name=contact_a.display_name,
                            contact_b_id=contact_b.id,
                            contact_b_name=contact_b.display_name,
                            score=min(score, 95.0),  # Cap at 95
                            reason=reason,
                            connection_type=conn_type,
                        )
                        pairs.append(pair)

            # Sort by score and return top-k
            pairs.sort(key=lambda x: x.score, reverse=True)
            return pairs[:top_k]

        except Exception as e:
            logger.error(f"Error finding connections: {e}")
            return []
        finally:
            if is_local_db:
                db.close()

    def _count_shared_items(self, mem_a: ContactMemory, mem_b: ContactMemory) -> int:
        """Count shared skills/interests between two memories."""
        count = 0

        # Helper to unwrap dict format {"skills": [...]} or {"interests": [...]}
        def unwrap_to_list(value):
            if isinstance(value, dict):
                # Try common keys
                for key in ["skills", "interests"]:
                    if key in value:
                        return value[key]
                return []
            elif isinstance(value, list):
                return value
            return []

        if mem_a.skills and mem_b.skills:
            skills_a = set(s.lower() for s in unwrap_to_list(mem_a.skills))
            skills_b = set(s.lower() for s in unwrap_to_list(mem_b.skills))
            count += len(skills_a & skills_b)

        if mem_a.interest and mem_b.interest:
            interests_a = set(s.lower() for s in unwrap_to_list(mem_a.interest))
            interests_b = set(s.lower() for s in unwrap_to_list(mem_b.interest))
            count += len(interests_a & interests_b)

        return count

    def suggest_connections_for_contact(
        self,
        contact_id: uuid.UUID,
        db: Session | None = None,
        top_k: int = 3,
    ) -> list[ConnectionPair]:
        """
        Tìm connections cho một contact cụ thể.

        Args:
            contact_id: UUID của contact cần tìm connection
            db: Database session
            top_k: Số connections tối đa

        Returns:
            List of ConnectionPair
        """

        is_local_db = db is None
        db = db or SessionLocal()

        try:
            # Get the contact
            contact = db.get(Contact, contact_id)
            if not contact:
                return []

            # Get all other contacts of the same user
            other_contacts = (
                db.query(Contact)
                .filter(
                    Contact.user_id == contact.user_id,
                    Contact.id != contact_id,
                )
                .all()
            )

            if not other_contacts:
                return []

            # Get memory for source contact
            source_memory = db.query(ContactMemory).filter(
                ContactMemory.contact_id == contact_id
            ).first()

            # Build pairs
            pairs: list[ConnectionPair] = []
            memories = {
                c.id: db.query(ContactMemory).filter(ContactMemory.contact_id == c.id).first()
                for c in other_contacts
            }

            for other_contact in other_contacts:
                should_connect, reason, conn_type = self._generate_connection_reasoning(
                    contact,
                    other_contact,
                    source_memory,
                    memories.get(other_contact.id),
                )

                if should_connect:
                    score = 70.0
                    if source_memory and memories.get(other_contact.id):
                        score += 15.0
                        shared = self._count_shared_items(source_memory, memories[other_contact.id])
                        score += min(shared * 5, 15.0)

                    pair = ConnectionPair(
                        contact_a_id=contact_id,
                        contact_a_name=contact.display_name,
                        contact_b_id=other_contact.id,
                        contact_b_name=other_contact.display_name,
                        score=min(score, 95.0),
                        reason=reason,
                        connection_type=conn_type,
                    )
                    pairs.append(pair)

            pairs.sort(key=lambda x: x.score, reverse=True)
            return pairs[:top_k]

        except Exception as e:
            logger.error(f"Error suggesting connections: {e}")
            return []
        finally:
            if is_local_db:
                db.close()
