from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    conversation_id: str = Field(description="ID của conversation nếu đã từng chat", default="")
    user_id: str = Field(description="UUID của user đối tác", default="")
    has_chatted: bool = Field(description="True nếu đã từng chat, False nếu chưa từng chat bao giờ", default=False)
    name: str = Field(description="Tên của đối tác")
    email: str = Field(description="Email của đối tác", default="")
    profession: str = Field(description="Nghề nghiệp / Chuyên môn", default="")
    company: str = Field(description="Công ty / Nơi làm việc", default="")
    skills: list[str] = Field(description="Kỹ năng chính", default_factory=list)
    interests: list[str] = Field(description="Chủ đề quan tâm / Sở thích", default_factory=list)
    tags: list[str] = Field(description="Các tag phân loại (ví dụ: Bạn bè, Khách hàng...)", default_factory=list)
    score: int = Field(description="Điểm đánh giá độ liên quan từ 0-100", default=0)
    explanation: str = Field(description="Giải thích lý do người này phù hợp với query", default="")
