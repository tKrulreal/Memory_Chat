import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.core.security import get_current_user
from src.models.user import User
from src.repositories.contact import ContactRepository
from src.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from src.schemas.pagination import PaginatedResponse, Pagination
from src.services.contact import ContactNotFoundError, ContactOwnershipError, ContactService

router = APIRouter()


def get_contact_service() -> ContactService:
    return ContactService(ContactRepository())


ContactServiceDep = Annotated[ContactService, Depends(get_contact_service)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
DatabaseDep = Annotated[Session, Depends(get_db)]


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
