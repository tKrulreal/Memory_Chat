from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    contact_id: str = Field(description="ID của contact")
    name: str = Field(description="Tên của contact")
    score: int = Field(description="Điểm đánh giá độ liên quan từ 0-100")
    explanation: str = Field(description="Giải thích lý do contact này phù hợp với query")
