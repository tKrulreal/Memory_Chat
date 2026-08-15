from pydantic import BaseModel
from src.schemas.conversation import ParticipantResponse

class SearchResult(BaseModel):
    conversation_id: str
    peer: ParticipantResponse
    summary_snippet: str | None = None
    score: float
