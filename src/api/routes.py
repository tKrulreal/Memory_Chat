from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/status")
async def agent_status():
    """Kiểm tra trạng thái agent."""
    return {"status": "ready", "agent": "Copilot Agent v2.0 (P2P)"}
