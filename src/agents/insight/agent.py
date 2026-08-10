import json
import logging
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel
import uuid

from sqlalchemy.orm import Session
from src.models.database import SessionLocal
from src.models.contact import ContactMemory
from src.gateways.llm import LLMGateway

logger = logging.getLogger(__name__)

class InsightType(str, Enum):
    INTEREST_PATTERN = "INTEREST_PATTERN"
    COMMUNICATION_STYLE = "COMMUNICATION_STYLE"
    RELATIONSHIP_TREND = "RELATIONSHIP_TREND"

class Insight(BaseModel):
    type: InsightType
    description: str

class InsightAgent:
    def __init__(self, llm: Optional[LLMGateway] = None):
        self._llm = llm or LLMGateway()

    async def generate_insights(self, contact_id: uuid.UUID) -> List[Insight]:
        db: Session = SessionLocal()
        try:
            # 1. Fetch Contact Memory
            memory = db.query(ContactMemory).filter(ContactMemory.contact_id == contact_id).first()
            if not memory:
                logger.warning(f"No memory found for contact {contact_id}")
                return []
            
            # 2. Build prompt
            memory_data = {
                "summary": memory.summary,
                "profession": memory.profession,
                "skills": memory.skills,
                "interest": memory.interest,
                "timeline": memory.timeline,
                "relationship_score": memory.relationship_score
            }
            prompt = f"""
            Dựa trên thông tin ghi nhớ sau về một liên hệ, hãy phân tích và tạo ra tối đa 3 insight (hiểu biết sâu sắc) về người này.
            Thông tin: {json.dumps(memory_data, ensure_ascii=False)}
            
            Các loại insight được phép:
            - INTEREST_PATTERN: Xu hướng quan tâm (VD: Người này thường xuyên nhắc đến AI).
            - COMMUNICATION_STYLE: Phong cách giao tiếp (VD: Người này thích nhắn tin ngắn gọn, trực tiếp).
            - RELATIONSHIP_TREND: Xu hướng mối quan hệ (VD: Điểm quan hệ đang tăng, cho thấy sự gắn kết).
            
            Trả về CHỈ một mảng JSON các object theo định dạng:
            [
              {{"type": "loại insight", "description": "mô tả ngắn gọn dưới 30 chữ"}}
            ]
            Nếu không đủ dữ liệu để phân tích, hãy trả về mảng rỗng [].
            """
            
            # 3. Call LLM
            response_text = self._llm.complete(prompt).strip()
            
            # Remove markdown JSON block if present
            if response_text.startswith("```json"):
                response_text = response_text.strip("```json").strip("```").strip()
            elif response_text.startswith("```"):
                response_text = response_text.strip("```").strip()
            
            # 4. Parse and return
            try:
                data = json.loads(response_text)
                insights = [Insight(**item) for item in data]
                
                # Update ContactMemory with new insights
                memory.insights = [insight.dict() for insight in insights]
                db.commit()
                
                return insights
            except Exception as parse_error:
                logger.error(f"Failed to parse LLM insight response: {response_text}. Error: {parse_error}")
                return []
                
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []
        finally:
            db.close()
