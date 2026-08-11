import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_event_bus
from src.events.bus import EventBus
from src.events.types import EventType

from src.core.security import get_current_user
from src.models.user import User
from src.repositories.contact import ContactRepository
from src.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from src.schemas.pagination import PaginatedResponse, Pagination
from src.services.contact import ContactNotFoundError, ContactOwnershipError, ContactService
from src.agents.insight.agent import InsightAgent
from pydantic import BaseModel, Field
import datetime


router = APIRouter()


def get_contact_service() -> ContactService:
    return ContactService(ContactRepository())

def get_insight_agent() -> InsightAgent:
    return InsightAgent()

ContactServiceDep = Annotated[ContactService, Depends(get_contact_service)]
InsightAgentDep = Annotated[InsightAgent, Depends(get_insight_agent)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
DatabaseDep = Annotated[Session, Depends(get_db)]
EventBusDep = Annotated[EventBus, Depends(get_event_bus)]

class InsightItemResponse(BaseModel):
    type: str
    description: str
    generated_at: str | None = None

class InsightListResponse(BaseModel):
    insights: list[InsightItemResponse]


@router.get("", response_model=PaginatedResponse[ContactResponse])
def list_contacts(
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ContactServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    search: str | None = None,
):
    contacts, total = service.get_user_contacts(db, current_user.id, page, limit, search)
    return PaginatedResponse(
        data=[service.to_response(contact) for contact in contacts],
        pagination=Pagination(page=page, limit=limit, total=total),
    )


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact_in: ContactCreate,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ContactServiceDep,
):
    return service.to_response(service.create_contact(db, current_user.id, contact_in))


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ContactServiceDep,
):
    return service.to_response(_get_owned_contact(service, db, current_user.id, contact_id))


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: uuid.UUID,
    contact_in: ContactUpdate,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ContactServiceDep,
):
    try:
        contact = service.update_contact(db, current_user.id, contact_id, contact_in)
    except ContactNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found") from None
    except ContactOwnershipError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this contact") from None
    return service.to_response(contact)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ContactServiceDep,
) -> Response:
    try:
        service.delete_contact(db, current_user.id, contact_id)
    except ContactNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found") from None
    except ContactOwnershipError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this contact") from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _get_owned_contact(
    service: ContactService,
    db: Session,
    user_id: uuid.UUID,
    contact_id: uuid.UUID,
):
    try:
        return service.get_owned_contact(db, user_id, contact_id)
    except ContactNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found") from None
    except ContactOwnershipError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this contact") from None


@router.get("/{contact_id}/insights", response_model=InsightListResponse)
def get_contact_insights(
    contact_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ContactServiceDep,
    agent: InsightAgentDep,
):
    # Verify ownership
    _get_owned_contact(service, db, current_user.id, contact_id)
    
    from src.services.memory import MemoryService
    memory = MemoryService.get_by_contact(db, contact_id)
    
    insights = []
    if memory and memory.insights:
        generated_at = memory.updated_at.isoformat() if memory.updated_at else datetime.datetime.now().isoformat()
        for i in memory.insights:
            insights.append(InsightItemResponse(
                type=i.get("type", ""),
                description=i.get("description", ""),
                generated_at=generated_at
            ))
            
    return InsightListResponse(insights=insights)

@router.post("/{contact_id}/insights/refresh", status_code=status.HTTP_202_ACCEPTED)
async def refresh_contact_insights(
    contact_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ContactServiceDep,
    event_bus: EventBusDep,
    agent: InsightAgentDep,
):
    # Verify ownership
    _get_owned_contact(service, db, current_user.id, contact_id)

    # Emit event to trigger background InsightWorker
    await event_bus.publish(
        event_type=EventType.MEMORY_UPDATED,
        user_id=current_user.id,
        payload={"contact_id": str(contact_id)}
    )


    return {"status": "refresh_triggered", "contact_id": str(contact_id)}


# =============================================================================
# Tagging Endpoints (TASK-COP-03)
# =============================================================================

class TagListResponse(BaseModel):
    tags: list[str]


class TagApproveRequest(BaseModel):
    tags: list[str] = Field(..., min_length=1, description="List of tag names to approve")


@router.get("/{contact_id}/tags", response_model=TagListResponse)
def get_contact_tags(
    contact_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ContactServiceDep,
) -> TagListResponse:
    """Lấy danh sách tags của một contact."""
    _get_owned_contact(service, db, current_user.id, contact_id)

    from src.agents.tagging import TaggingAgent
    agent = TaggingAgent()
    tags = agent.get_contact_tags(db, contact_id)
    return TagListResponse(tags=tags)


@router.get("/{contact_id}/suggested-tags", response_model=TagListResponse)
async def get_suggested_tags(
    contact_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ContactServiceDep,
) -> TagListResponse:
    """
    Đề xuất tags cho contact dựa trên Memory.

    Gọi TaggingAgent để phân tích memory và đề xuất tags phù hợp.
    """
    _get_owned_contact(service, db, current_user.id, contact_id)

    from src.agents.tagging import TaggingAgent
    agent = TaggingAgent()
    suggested = await agent.suggest_tags(contact_id, db)
    return TagListResponse(tags=suggested)


@router.post("/{contact_id}/tags", response_model=TagListResponse, status_code=status.HTTP_201_CREATED)
async def approve_contact_tags(
    contact_id: uuid.UUID,
    request: TagApproveRequest,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ContactServiceDep,
) -> TagListResponse:
    """
    User approve tags → lưu vào ContactTag.

    Tags đã approve sẽ được gắn vào contact.
    """
    _get_owned_contact(service, db, current_user.id, contact_id)

    from src.agents.tagging import TaggingAgent
    agent = TaggingAgent()
    saved_tags = await agent.approve_tags(db, contact_id, request.tags)
    return TagListResponse(tags=[t.name for t in saved_tags])


@router.delete("/{contact_id}/tags/{tag_name}", status_code=status.HTTP_204_NO_CONTENT)
def remove_contact_tag(
    contact_id: uuid.UUID,
    tag_name: str,
    current_user: CurrentUserDep,
    db: DatabaseDep,
    service: ContactServiceDep,
) -> Response:
    """Xóa một tag khỏi contact."""
    _get_owned_contact(service, db, current_user.id, contact_id)

    from src.models.contact import Tag, Contact
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Find and remove tag
    for tag in contact.tags:
        if tag.name == tag_name:
            contact.tags.remove(tag)
            db.commit()
            break

    return Response(status_code=status.HTTP_204_NO_CONTENT)

