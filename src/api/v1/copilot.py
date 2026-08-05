from fastapi import APIRouter, Depends, status
from typing import Any

router = APIRouter()

@router.post("/chat", response_model=Any)
async def copilot_chat(payload: dict):
    """AI Copilot interaction endpoint."""
    return {"reply": "Mock copilot response", "context": payload}
