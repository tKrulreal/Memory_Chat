from pydantic import BaseModel, Field

class AIContext(BaseModel):
    summary: str | None = None
    last_met: str | None = None
    interested_in: list[str] = Field(default_factory=list)
    follow_up: str | None = None
