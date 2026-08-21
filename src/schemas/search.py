import uuid
from typing import Literal

from pydantic import BaseModel

from src.schemas.conversation import ParticipantResponse

# ── existing conversation search ────────────────────────────────────────────
class SearchResult(BaseModel):
    conversation_id: str
    peer: ParticipantResponse
    summary_snippet: str | None = None
    score: float


# ── new user / people search ─────────────────────────────────────────────────
UserRelation = Literal["none", "pending_sent", "pending_received", "friend"]


class UserSearchResult(BaseModel):
    id: uuid.UUID
    full_name: str | None
    email: str
    avatar: str | None
    relation: UserRelation
    conversation_id: uuid.UUID | None


class UserSearchResponse(BaseModel):
    items: list[UserSearchResult]
    total: int
    limit: int
    offset: int
