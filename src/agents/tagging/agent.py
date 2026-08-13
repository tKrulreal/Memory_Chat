"""
Tagging Agent — đề xuất tags cho Contact từ Memory.

Agent này trích xuất entities từ Memory và đề xuất tags
phù hợp cho user approve.
"""

import json
import logging
import uuid

from sqlalchemy.orm import Session

from src.gateways.llm import LLMGateway
from src.models.contact import Contact, ContactMemory, Tag

logger = logging.getLogger(__name__)

# Prompt cho Tagging Agent
TAG_EXTRACTION_PROMPT = """Bạn là một Tagging Agent cho hệ thống nhắn tin MemoryChat.

Nhiệm vụ: Từ thông tin ghi nhớ (memory) của một contact, đề xuất 3-5 tags phù hợp.

Rules:
- Tags phải là lowercase, không có khoảng trắng (dùng underscore _ nếu cần)
- Tags phải ngắn gọn, dễ hiểu
- Tags nên phản ánh: profession, industry, skill, interest, topic
- KHÔNG đề xuất tags nhạy cảm (religion, politics, health issues)

Ví dụ tags tốt:
- ai_engineer, software_developer, startup_founder
- blockchain, data_science, product_management
- investor, mentor, vinuni_alumni

Memory info:
{memory_info}

CHỈ trả về JSON array các tags:
["tag1", "tag2", "tag3"]

Không có text khác, chỉ JSON array."""


class TaggingAgent:
    def __init__(self, llm: LLMGateway | None = None):
        self._llm = llm or LLMGateway()

    def _build_memory_context(self, memory: ContactMemory) -> str:
        """Build readable context string từ memory."""
        parts = []

        if memory.summary:
            parts.append(f"Summary: {memory.summary}")

        if memory.profession:
            parts.append(f"Profession: {memory.profession}")

        if memory.company:
            parts.append(f"Company: {memory.company}")

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

        if memory.timeline:
            parts.append(f"Timeline: {memory.timeline}")

        return "\n".join(parts) if parts else "No memory data available"

    async def suggest_tags(
        self,
        contact_id: uuid.UUID,
        db: Session | None = None,
        max_tags: int = 5,
    ) -> list[str]:
        """
        Đề xuất tags cho một contact.

        Args:
            contact_id: UUID của contact
            db: Database session (optional)
            max_tags: Số tags tối đa (mặc định 5)

        Returns:
            List of suggested tag names
        """
        from src.models.database import SessionLocal

        is_local_db = db is None
        db = db or SessionLocal()

        try:
            # Get memory
            memory = db.query(ContactMemory).filter(
                ContactMemory.contact_id == contact_id
            ).first()

            if not memory:
                logger.info(f"No memory for contact {contact_id}, cannot suggest tags")
                return []

            # Build context
            memory_context = self._build_memory_context(memory)

            # Call LLM
            prompt = TAG_EXTRACTION_PROMPT.format(memory_info=memory_context)

            try:
                response = self._llm.complete(prompt).strip()

                # Parse JSON response
                if response.startswith("```json"):
                    response = response.strip("```json").strip("```").strip()
                elif response.startswith("```"):
                    response = response.strip("```").strip()

                tags = json.loads(response)

                # Validate tags
                if not isinstance(tags, list):
                    logger.warning(f"Unexpected tags format: {tags}")
                    return []

                # Clean and validate tags
                cleaned_tags = []
                for tag in tags[:max_tags]:
                    if isinstance(tag, str) and len(tag) > 0 and len(tag) <= 50:
                        # Normalize: lowercase, no spaces
                        normalized = tag.lower().strip().replace(" ", "_")
                        if normalized and normalized not in cleaned_tags:
                            cleaned_tags.append(normalized)

                logger.info(f"Suggested {len(cleaned_tags)} tags for contact {contact_id}: {cleaned_tags}")
                return cleaned_tags

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse tags JSON: {e}, response: {response}")
                return []
            except Exception as e:
                logger.error(f"LLM call failed for tag suggestion: {e}")
                return []

        finally:
            if is_local_db:
                db.close()

    def get_or_create_tags(
        self,
        db: Session,
        tag_names: list[str],
    ) -> list[Tag]:
        """
        Get existing tags or create new ones.

        Args:
            db: Database session
            tag_names: List of tag names

        Returns:
            List of Tag objects
        """
        tags = []

        for name in tag_names:
            # Try to find existing tag
            tag = db.query(Tag).filter(Tag.name == name).first()

            if not tag:
                # Create new tag
                tag = Tag(name=name)
                db.add(tag)

            tags.append(tag)

        db.commit()
        return tags

    async def approve_tags(
        self,
        db: Session,
        contact_id: uuid.UUID,
        tag_names: list[str],
    ) -> list[Tag]:
        """
        User approve tags → save to ContactTag.

        Args:
            db: Database session
            contact_id: UUID của contact
            tag_names: List of tag names user approved

        Returns:
            List of saved Tag objects
        """
        # Get or create tags
        tags = self.get_or_create_tags(db, tag_names)

        # Get contact
        contact = db.get(Contact, contact_id)
        if not contact:
            raise ValueError(f"Contact {contact_id} not found")

        # Add tags to contact (many-to-many)
        existing_tag_names = {t.name for t in contact.tags}
        for tag in tags:
            if tag.name not in existing_tag_names:
                contact.tags.append(tag)

        db.commit()

        logger.info(f"Approved {len(tags)} tags for contact {contact_id}: {tag_names}")
        return tags

    def get_contact_tags(
        self,
        db: Session,
        contact_id: uuid.UUID,
    ) -> list[str]:
        """
        Get current tags của một contact.

        Args:
            db: Database session
            contact_id: UUID của contact

        Returns:
            List of tag names
        """
        contact = db.get(Contact, contact_id)
        if not contact:
            return []

        return [tag.name for tag in contact.tags]
