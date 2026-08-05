from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any

router = APIRouter()

@router.post("/", response_model=Any, status_code=status.HTTP_201_CREATED)
async def send_message(message_in: dict):
    """Send a new message to a conversation."""
    return {"id": "mock_msg_id", **message_in}

@router.get("/{message_id}", response_model=Any)
async def get_message(message_id: str):
    """Get a specific message by ID."""
    return {"id": message_id, "content": "Mock message content"}
