from typing import Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class Pagination(BaseModel):
    page: int = Field(ge=1)
    limit: int = Field(ge=1)
    total: int = Field(ge=0)


class PaginatedResponse(BaseModel, Generic[DataT]):
    data: list[DataT]
    pagination: Pagination


class CursorPagination(BaseModel):
    has_next: bool
    limit: int


class CursorPaginatedResponse(BaseModel, Generic[DataT]):
    data: list[DataT]
    pagination: CursorPagination
