from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int

    @property
    def has_more(self) -> bool:
        return self.skip + self.limit < self.total


class MessageResponse(BaseModel):
    message: str


class IDResponse(BaseModel):
    id: int
