from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class AIContext(BaseModel):
    model_config = ConfigDict(extra="ignore")

    summary: str | None = None
    last_met: str | None = None
    interested_in: list[str] = Field(default_factory=list)
    follow_up: str | None = None
    tags: list[str] = Field(default_factory=list)
    pending_tags: list[str] = Field(default_factory=list)
    relationship_score: int | None = None
    timeline: list[dict[str, Any]] | None = None
