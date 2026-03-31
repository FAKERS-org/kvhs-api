"""
CMS-related schemas.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DepartmentBase(BaseModel):
    """Shared department fields."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class DepartmentCreate(DepartmentBase):
    """Department creation schema."""


class DepartmentUpdate(BaseModel):
    """Department update schema."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class DepartmentRead(DepartmentBase):
    """Department response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class ContentTagBase(BaseModel):
    """Shared content tag fields."""

    name: str = Field(..., min_length=1, max_length=100)


class ContentTagCreate(ContentTagBase):
    """Content tag creation schema."""


class ContentTagRead(ContentTagBase):
    """Content tag response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime


class ContentBase(BaseModel):
    """Shared content fields."""

    title: str = Field(..., min_length=1, max_length=500)
    slug: str = Field(..., min_length=1, max_length=500)
    content_type: str = Field(..., min_length=1, max_length=50)
    body: str
    template: str | None = Field(default=None, max_length=100)
    status: str = Field(default="draft")
    department_id: str | None = None
    course_id: int | None = None
    parent_id: str | None = None


class ContentCreate(ContentBase):
    """Content creation schema."""

    tag_ids: list[str] = Field(default_factory=list)


class ContentUpdate(BaseModel):
    """Content update schema."""

    title: str | None = Field(default=None, min_length=1, max_length=500)
    slug: str | None = Field(default=None, min_length=1, max_length=500)
    content_type: str | None = Field(default=None, min_length=1, max_length=50)
    body: str | None = None
    template: str | None = None
    status: str | None = None
    department_id: str | None = None
    course_id: int | None = None
    parent_id: str | None = None
    tag_ids: list[str] | None = None


class ContentRead(ContentBase):
    """Content response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    author_teacher_id: int | None
    author_admin_id: int | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    tags: list[ContentTagRead] = []


class DocumentBase(BaseModel):
    """Shared document fields."""

    title: str = Field(..., min_length=1, max_length=500)
    filename: str = Field(..., min_length=1, max_length=500)
    gridfs_id: str = Field(..., min_length=1, max_length=500)
    file_size: int
    mime_type: str = Field(..., min_length=1, max_length=100)
    content_id: str | None = None
    course_id: int | None = None


class DocumentCreate(DocumentBase):
    """Document creation schema."""


class DocumentUpdate(BaseModel):
    """Document update schema."""

    title: str | None = Field(default=None, min_length=1, max_length=500)
    content_id: str | None = None
    course_id: int | None = None


class DocumentRead(DocumentBase):
    """Document response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    uploaded_by_teacher_id: int | None
    uploaded_by_admin_id: int | None
    created_at: datetime
    updated_at: datetime


class CalendarEventBase(BaseModel):
    """Shared calendar event fields."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    event_type: str = Field(..., min_length=1, max_length=50)
    start_date: datetime
    end_date: datetime
    all_day: bool = False
    course_id: int | None = None
    department_id: str | None = None


class CalendarEventCreate(CalendarEventBase):
    """Calendar event creation schema."""


class CalendarEventUpdate(BaseModel):
    """Calendar event update schema."""

    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    event_type: str | None = Field(default=None, min_length=1, max_length=50)
    start_date: datetime | None = None
    end_date: datetime | None = None
    all_day: bool | None = None
    course_id: int | None = None
    department_id: str | None = None


class CalendarEventRead(CalendarEventBase):
    """Calendar event response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_by_teacher_id: int | None
    created_by_admin_id: int | None
    created_at: datetime
    updated_at: datetime
