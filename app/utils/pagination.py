from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams:
    def __init__(
        self,
        limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
        offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    ) -> None:
        self.limit = limit
        self.offset = offset


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    items: list[T]
