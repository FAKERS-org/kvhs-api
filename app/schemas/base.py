"""
Base schemas and common types.
"""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


# Custom types
EmailStr = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=255,
        pattern=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
    ),
]


# Base response schema
class BaseResponse(BaseModel):
    """Base response schema with common configuration."""

    model_config = ConfigDict(from_attributes=True)


# Timestamp mixin
class TimestampSchema(BaseModel):
    """Schema mixin for timestamps."""

    created_at: datetime
    updated_at: datetime


# Pagination schemas
class PaginationParams(BaseModel):
    """Pagination parameters."""

    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    items: list
    total: int
    skip: int
    limit: int
    has_more: bool
