from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any

router = APIRouter()

@router.get("/contacts/{contact_id}", response_model=Any)
async def get_contact_memory(contact_id: str):
    """Get memory summary for a contact."""
    return {"contact_id": contact_id, "summary": "Mock memory summary."}

@router.post("/trigger", response_model=Any)
async def trigger_memory_extraction(payload: dict):
    """Manually trigger memory extraction for a conversation."""
    return {"status": "triggered", "conversation_id": payload.get("conversation_id")}
