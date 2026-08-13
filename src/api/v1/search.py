from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.agents.search import SearchAgent
from src.api.deps import get_db
from src.core.security import get_current_user
from src.models.user import SearchHistory, User
from src.schemas.search import SearchAPIResponse

router = APIRouter()

def get_search_agent() -> SearchAgent:
    return SearchAgent()

@router.get("", response_model=SearchAPIResponse)
async def semantic_search(
    q: str = Query(..., min_length=3, description="Search query"),
    limit: int = Query(5, ge=1, le=20, description="Max results to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    agent: SearchAgent = Depends(get_search_agent)
):
    """Semantic search across memories and contacts."""
    try:
        results = await agent.search(q, limit=limit)
    except Exception:
        # Tạm thời log exception hoặc bọc lại, ở đây nếu lỗi trả [] theo requirement
        results = []

    # Lưu lịch sử tìm kiếm vào DB
    try:
        # Serialize list of SearchResult to dict
        results_json = [r.model_dump() for r in results]

        history_record = SearchHistory(
            user_id=current_user.id,
            query=q,
            results=results_json,
            result_count=len(results)
        )
        db.add(history_record)
        db.commit()
    except Exception:
        db.rollback()
        # Vẫn trả kết quả search cho user kể cả khi log lỗi

    return SearchAPIResponse(query=q, results=results)
