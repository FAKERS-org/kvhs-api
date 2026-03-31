"""
CMS models using Beanie for MongoDB (unstructured data).
"""

from datetime import datetime
from typing import Optional

from beanie import Document as BeanieDocument
from pydantic import Field


class Department(BeanieDocument):
    """Department model for content organization."""

    name: str = Field(..., unique=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "departments"


class ContentTag(BeanieDocument):
    """Content tag model."""

    name: str = Field(..., unique=True)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "content_tags"


class Content(BeanieDocument):
    """Main Content model for CMS."""

    title: str
    slug: str = Field(..., unique=True)
    content_type: str
    body: str  # Can be JSON or rich text
    template: Optional[str] = None
    status: str = "draft"
    published_at: Optional[datetime] = None

    # Foreign references (SQL IDs)
    department_id: Optional[str] = None  # Reference to Department in MongoDB
    course_id: Optional[int] = None  # Reference to Course in SQL
    parent_id: Optional[str] = None  # Reference to Content in MongoDB

    # Author tracking (SQL IDs)
    author_teacher_id: Optional[int] = None
    author_admin_id: Optional[int] = None

    # Tags (MongoDB IDs)
    tag_ids: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "contents"


class CMSDocument(BeanieDocument):
    """Document model for file attachments."""

    title: str
    filename: str
    gridfs_id: str
    file_size: int
    mime_type: str

    # Organization
    content_id: Optional[str] = None  # Reference to Content in MongoDB
    course_id: Optional[int] = None  # Reference to Course in SQL

    # Upload tracking (SQL IDs)
    uploaded_by_teacher_id: Optional[int] = None
    uploaded_by_admin_id: Optional[int] = None

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "documents"


class CalendarEvent(BeanieDocument):
    """Calendar event model."""

    title: str
    description: Optional[str] = None
    event_type: str
    start_date: datetime
    end_date: datetime
    all_day: bool = False

    # Organization
    course_id: Optional[int] = None  # Reference to Course in SQL
    department_id: Optional[str] = None  # Reference to Department in MongoDB

    # Author tracking (SQL IDs)
    created_by_teacher_id: Optional[int] = None
    created_by_admin_id: Optional[int] = None

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "calendar_events"
