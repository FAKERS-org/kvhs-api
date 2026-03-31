"""
Search-related schemas.
"""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Search request schema."""

    query: str = Field(..., min_length=1)
    content_type: str | None = None
    department_id: int | None = None
    tags: list[str] = Field(default_factory=list)
    status: str | None = None
