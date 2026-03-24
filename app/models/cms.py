"""
CMS models (Content, Document, Calendar, Department, Tag).
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import PublishStatus
from app.models.base import Base, TimestampMixin


class Department(Base, TimestampMixin):
    """Department model for content organization."""

    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    contents: Mapped[list["Content"]] = relationship(back_populates="department")
    calendar_events: Mapped[list["CalendarEvent"]] = relationship(
        back_populates="department"
    )


class ContentTag(Base, TimestampMixin):
    """Content tag model."""

    __tablename__ = "content_tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)


class ContentTagAssociation(Base):
    """Association table for Content and Tags (many-to-many)."""

    __tablename__ = "content_tag_associations"

    content_id: Mapped[int] = mapped_column(ForeignKey("contents.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("content_tags.id"), primary_key=True)


class Content(Base, TimestampMixin):
    """Main Content model for CMS."""

    __tablename__ = "contents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    slug: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    content_type: Mapped[str] = mapped_column(String(50), index=True)
    body: Mapped[str] = mapped_column(Text)
    template: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Publishing
    status: Mapped[str] = mapped_column(
        String(20), default=PublishStatus.DRAFT.value, index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Organization
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id"), nullable=True, index=True
    )
    course_id: Mapped[int | None] = mapped_column(
        ForeignKey("courses.id"), nullable=True, index=True
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("contents.id"), nullable=True, index=True
    )

    # Author tracking
    author_teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.id"), nullable=True, index=True
    )
    author_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("admins.id"), nullable=True, index=True
    )

    # Relationships
    department: Mapped["Department | None"] = relationship(back_populates="contents")
    course: Mapped["Course | None"] = relationship(back_populates="contents")
    author: Mapped["Teacher | None"] = relationship(back_populates="contents")
    admin_author: Mapped["Admin | None"] = relationship(back_populates="contents")

    # Hierarchical relationship
    parent: Mapped["Content | None"] = relationship(
        "Content", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["Content"]] = relationship("Content", back_populates="parent")

    # Tags (many-to-many)
    tags: Mapped[list["ContentTag"]] = relationship(
        secondary="content_tag_associations", lazy="selectin"
    )

    # Documents
    documents: Mapped[list["Document"]] = relationship(
        back_populates="content", cascade="all, delete-orphan"
    )


class Document(Base, TimestampMixin):
    """Document model for file attachments."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    filename: Mapped[str] = mapped_column(String(500))
    file_path: Mapped[str] = mapped_column(String(1000))
    file_size: Mapped[int] = mapped_column(Integer)
    mime_type: Mapped[str] = mapped_column(String(100))

    # Organization
    content_id: Mapped[int | None] = mapped_column(
        ForeignKey("contents.id"), nullable=True, index=True
    )
    course_id: Mapped[int | None] = mapped_column(
        ForeignKey("courses.id"), nullable=True, index=True
    )

    # Upload tracking
    uploaded_by_teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.id"), nullable=True, index=True
    )
    uploaded_by_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("admins.id"), nullable=True, index=True
    )

    # Relationships
    content: Mapped["Content | None"] = relationship(back_populates="documents")
    course: Mapped["Course | None"] = relationship(back_populates="documents")


class CalendarEvent(Base, TimestampMixin):
    """Calendar event model."""

    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)

    # Date/Time
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    all_day: Mapped[bool] = mapped_column(default=False)

    # Organization
    course_id: Mapped[int | None] = mapped_column(
        ForeignKey("courses.id"), nullable=True, index=True
    )
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id"), nullable=True, index=True
    )

    # Author tracking
    created_by_teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.id"), nullable=True, index=True
    )
    created_by_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("admins.id"), nullable=True, index=True
    )

    # Relationships
    course: Mapped["Course | None"] = relationship(back_populates="calendar_events")
    department: Mapped["Department | None"] = relationship(
        back_populates="calendar_events"
    )
