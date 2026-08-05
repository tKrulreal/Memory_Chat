from fastapi import APIRouter, Depends, Query
from typing import List, Any

router = APIRouter()

@router.get("/", response_model=List[Any])
async def semantic_search(q: str = Query(..., description="Search query")):
    """Semantic search across memories and messages."""
    return [{"result": "Mock search result", "query": q}]
