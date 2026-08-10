import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import Session

from src.models.database import SessionLocal
from src.models.contact import Contact, ContactMemory
from src.models.chat import Conversation, Message
from src.models.ai import Recommendation
from src.schemas.enums import RecommendationType, MessageRole
from src.gateways.llm import LLMGateway

logger = logging.getLogger(__name__)
VN_TZ = timezone(timedelta(hours=7))

class RecommendationAgent:
    def __init__(self, llm: Optional[LLMGateway] = None):
        self._llm = llm or LLMGateway()

    async def generate(self, user_id: uuid.UUID, db: Optional[Session] = None) -> List[Recommendation]:
        """
        Generate recommendations for all contacts of a specific user.
        (For production, we might want to run this incrementally or per contact)
        """
        is_local_db = db is None
        db = db or SessionLocal()
        new_recommendations = []
        try:
            # 1. Rule: PRIORITY - Memory relationship_score > 80
            priority_recs = self._check_priority_rule(db, user_id)
            new_recommendations.extend(priority_recs)

            # 2. Rule: FOLLOWUP - Idle > 7 days
            followup_recs = self._check_followup_rule(db, user_id)
            new_recommendations.extend(followup_recs)

            # 3. Rule: REPLY - Last message from contact > 24h ago
            reply_recs = self._check_reply_rule(db, user_id)
            new_recommendations.extend(reply_recs)

            # 4. Dedup & LLM Reasoning & Save
            saved_recs = []
            for rec in new_recommendations:
                # Check if same type of recommendation already exists and is PENDING
                existing = db.scalars(
                    select(Recommendation).where(
                        and_(
                            Recommendation.contact_id == rec.contact_id,
                            Recommendation.type == rec.type,
                            Recommendation.status == "PENDING"
                        )
                    )
                ).first()

                if not existing:
                    # Generate reasoning with LLM
                    contact = db.get(Contact, rec.contact_id)
                    reason = self._generate_reasoning(contact, rec.type)
                    rec.reason = reason
                    db.add(rec)
                    saved_recs.append(rec)
            
            if saved_recs:
                db.commit()
                for rec in saved_recs:
                    db.refresh(rec)
                
            return saved_recs
        except Exception as e:
            db.rollback()
            logger.error(f"Error generating recommendations: {e}")
            return []
        finally:
            if is_local_db:
                db.close()

    def _check_priority_rule(self, db: Session, user_id: uuid.UUID) -> List[Recommendation]:
        recs = []
        stmt = select(ContactMemory, Contact).join(Contact).where(
            and_(
                Contact.user_id == user_id,
                ContactMemory.relationship_score >= 80
            )
        )
        for memory, contact in db.execute(stmt).all():
            rec = Recommendation(
                contact_id=contact.id,
                type=RecommendationType.PRIORITY,
                priority="HIGH"
            )
            recs.append(rec)
        return recs

    def _check_followup_rule(self, db: Session, user_id: uuid.UUID) -> List[Recommendation]:
        recs = []
        seven_days_ago = datetime.now(VN_TZ) - timedelta(days=7)
        # Find conversations where last message was older than 7 days
        stmt = select(Conversation).where(
            and_(
                Conversation.user_id == user_id,
                Conversation.last_message_time != None,
                Conversation.last_message_time < seven_days_ago
            )
        )
        conversations = db.scalars(stmt).all()
        for conv in conversations:
            rec = Recommendation(
                contact_id=conv.contact_id,
                type=RecommendationType.FOLLOWUP,
                priority="MEDIUM"
            )
            recs.append(rec)
        return recs

    def _check_reply_rule(self, db: Session, user_id: uuid.UUID) -> List[Recommendation]:
        recs = []
        one_day_ago = datetime.now(VN_TZ) - timedelta(days=1)
        
        stmt = select(Conversation).where(
            and_(
                Conversation.user_id == user_id,
                Conversation.last_message_time != None,
                Conversation.last_message_time < one_day_ago
            )
        )
        conversations = db.scalars(stmt).all()
        for conv in conversations:
            # Check if last message was from CONTACT
            last_msg = db.scalars(
                select(Message)
                .where(Message.conversation_id == conv.id)
                .order_by(Message.created_at.desc())
                .limit(1)
            ).first()

            if last_msg and last_msg.sender_type == MessageRole.CONTACT:
                rec = Recommendation(
                    contact_id=conv.contact_id,
                    type=RecommendationType.REPLY,
                    priority="HIGH"
                )
                recs.append(rec)
        return recs

    def _generate_reasoning(self, contact: Contact, rec_type: str) -> str:
        prompt = f"""
        Tạo một câu lý do ngắn gọn (dưới 20 chữ) giải thích tại sao người dùng nên tương tác với '{contact.display_name}'.
        Loại hành động: {rec_type}.
        - Nếu là FOLLOWUP: Nên hỏi thăm vì lâu chưa nhắn.
        - Nếu là REPLY: Nên trả lời tin nhắn cũ vì họ đang đợi.
        - Nếu là PRIORITY: Đây là khách hàng/liên hệ quan trọng cần chú ý.
        Chỉ trả về câu lý do, không cần phần mở đầu hay kết luận.
        """
        try:
            return self._llm.complete(prompt).strip()
        except Exception:
            # Fallback text in case LLM fails
            if rec_type == RecommendationType.FOLLOWUP:
                return "Đã hơn 7 ngày chưa tương tác."
            elif rec_type == RecommendationType.REPLY:
                return "Họ đang chờ bạn trả lời tin nhắn."
            else:
                return "Đây là liên hệ quan trọng."
