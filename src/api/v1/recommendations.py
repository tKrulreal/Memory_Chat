import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from src.agents.recommendation.agent import RecommendationAgent
from src.api.deps import get_db
from src.core.security import get_current_user
from src.models.ai import Recommendation
from src.models.contact import Contact
from src.models.user import User
from src.schemas.recommendation import RecommendationResponse

router = APIRouter()

@router.get("/", response_model=list[RecommendationResponse])
async def get_recommendations(
    status: str = Query("PENDING", description="Lọc theo trạng thái: PENDING, ACCEPTED, REJECTED"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách các recommendations cho user hiện tại.
    """
    # Join with Contact to ensure the recommendation belongs to current_user
    stmt = (
        select(Recommendation, Contact.display_name)
        .join(Contact, Recommendation.contact_id == Contact.id)
        .where(Contact.user_id == current_user.id)
        .where(Recommendation.status == status)
        .order_by(desc(Recommendation.created_at))
        .offset(skip)
        .limit(limit)
    )

    results = db.execute(stmt).all()

    response = []
    for rec, display_name in results:
        rec_dict = {
            "id": rec.id,
            "contact_id": rec.contact_id,
            "type": rec.type,
            "reason": rec.reason,
            "priority": rec.priority,
            "status": rec.status,
            "created_at": rec.created_at,
            "contact_name": display_name
        }
        response.append(RecommendationResponse(**rec_dict))

    return response

@router.post("/{id}/accept")
async def accept_recommendation(
    request: Request,
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chấp nhận một recommendation.
    """
    stmt = select(Recommendation).join(Contact).where(
        Recommendation.id == id,
        Contact.user_id == current_user.id
    )
    rec = db.scalars(stmt).first()

    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if rec.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Cannot accept recommendation with status {rec.status}")

    rec.status = "ACCEPTED"
    db.commit()

    # Emit event
    if hasattr(request.app.state, "event_bus"):
        await request.app.state.event_bus.publish(
            "recommendation_accepted",
            {"recommendation_id": str(rec.id), "user_id": str(current_user.id), "contact_id": str(rec.contact_id)}
        )

    return {"status": "success", "message": "Recommendation accepted"}

@router.post("/{id}/reject")
async def reject_recommendation(
    request: Request,
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Từ chối một recommendation.
    """
    stmt = select(Recommendation).join(Contact).where(
        Recommendation.id == id,
        Contact.user_id == current_user.id
    )
    rec = db.scalars(stmt).first()

    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if rec.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Cannot reject recommendation with status {rec.status}")

    rec.status = "REJECTED"
    db.commit()

    # Emit event
    if hasattr(request.app.state, "event_bus"):
        await request.app.state.event_bus.publish(
            "recommendation_rejected",
            {"recommendation_id": str(rec.id), "user_id": str(current_user.id), "contact_id": str(rec.contact_id)}
        )

    return {"status": "success", "message": "Recommendation rejected"}

@router.post("/generate")
async def generate_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chạy RecommendationAgent để sinh ra các recommendations mới ngay lập tức.
    """
    agent = RecommendationAgent()
    recs = await agent.generate(user_id=current_user.id, db=db)
    return {"status": "success", "generated_count": len(recs)}
