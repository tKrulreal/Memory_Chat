from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any

router = APIRouter()

@router.get("/", response_model=List[Any])
async def list_conversations():
    """List all conversations for the current user."""
    return []

@router.post("/", response_model=Any, status_code=status.HTTP_201_CREATED)
async def create_conversation(conversation_in: dict):
    """Create a new conversation."""
    return {"id": "mock_conv_id", **conversation_in}

@router.get("/{conversation_id}", response_model=Any)
async def get_conversation(conversation_id: str):
    """Get conversation details by ID."""
    return {"id": conversation_id, "name": "Mock Conversation"}

@router.get("/{conversation_id}/messages", response_model=List[Any])
async def get_conversation_messages(conversation_id: str):
    """Get all messages in a conversation."""
    return []
