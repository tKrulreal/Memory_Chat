from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any

router = APIRouter()

@router.get("/", response_model=List[Any])
async def get_recommendations():
    """Get recommendations (follow-ups, replies, etc.) for the current user."""
    return []
