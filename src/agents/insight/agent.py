import json
import logging
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
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

