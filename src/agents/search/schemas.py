from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    conversation_id: str = Field(description="ID của conversation")
    name: str = Field(description="Tên của contact")
    email: str = Field(description="Email của contact", default="")
    score: int = Field(description="Điểm đánh giá độ liên quan từ 0-100")
    explanation: str = Field(description="Giải thích lý do contact này phù hợp với query")
