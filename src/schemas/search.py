from typing import List
from pydantic import BaseModel, Field
from src.agents.search.schemas import SearchResult

class SearchAPIResponse(BaseModel):
    query: str = Field(description="Truy vấn nguyên gốc")
    results: List[SearchResult] = Field(description="Danh sách kết quả tìm kiếm")
