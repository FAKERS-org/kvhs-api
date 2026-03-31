"""
CMS SQLAlchemy models for PostgreSQL.
Replaces Beanie MongoDB models.
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String,
    Text,
    Integer,
    ForeignKey,
    Table,
    Column,
    DateTime,
    Index,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


# Association table for Content-Tag many-to-many relationship
content_tags_association = Table(
    "content_content_tags",
    Base.metadata,
    Column("content_id", Integer, ForeignKey("cms_contents.id", ondelete="CASCADE"), primary_key=True),
    Column("content_tag_id", Integer, ForeignKey("cms_content_tags.id", ondelete="CASCADE"), primary_key=True),
)


class Department(Base, TimestampMixin):
    """Department model for content organization."""

    __tablename__ = "cms_departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    contents: Mapped[List["Content"]] = relationship(
        "Content", back_populates="department", foreign_keys="Content.department_id"
    )
    calendar_events: Mapped[List["CalendarEvent"]] = relationship(
        "CalendarEvent", back_populates="department"
    )

    __table_args__ = (
        Index("ix_cms_departments_name", "name", unique=True),
    )


class ContentTag(Base, TimestampMixin):
    """Content tag model."""

    __tablename__ = "cms_content_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    # Relationships
    contents: Mapped[List["Content"]] = relationship(
        "Content", secondary=content_tags_association, back_populates="tags"
    )

    __table_args__ = (
        Index("ix_cms_content_tags_name", "name", unique=True),
    )


class Content(Base, TimestampMixin):
    """Main Content model for CMS."""

    __tablename__ = "cms_contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    template: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Foreign references
    department_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("cms_departments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    course_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("cms_contents.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Author tracking (SQL IDs)
    author_teacher_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    author_admin_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    department: Mapped[Optional["Department"]] = relationship(
        "Department", back_populates="contents", foreign_keys=[department_id]
    )
    tags: Mapped[List["ContentTag"]] = relationship(
        "ContentTag", secondary=content_tags_association, back_populates="contents"
    )
    parent: Mapped[Optional["Content"]] = relationship(
        "Content", remote_side=[id], back_populates="children"
    )
    children: Mapped[List["Content"]] = relationship(
        "Content", remote_side=[parent_id], back_populates="parent"
    )
    documents: Mapped[List["CMSDocument"]] = relationship(
        "CMSDocument", back_populates="content"
    )

    __table_args__ = (
        Index("ix_cms_contents_slug", "slug", unique=True),
        Index("ix_cms_contents_status", "status"),
        Index("ix_cms_contents_content_type", "content_type"),
    )


class CMSDocument(Base, TimestampMixin):
    """Document model for file attachments (MinIO storage)."""

    __tablename__ = "cms_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    minio_object_name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Organization
    content_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("cms_contents.id", ondelete="CASCADE"), nullable=True, index=True
    )
    course_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    # Upload tracking (SQL IDs)
    uploaded_by_teacher_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    uploaded_by_admin_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    content: Mapped[Optional["Content"]] = relationship(
        "Content", back_populates="documents"
    )

    __table_args__ = (
        Index("ix_cms_documents_minio_object_name", "minio_object_name"),
    )


class CalendarEvent(Base, TimestampMixin):
    """Calendar event model."""

    __tablename__ = "cms_calendar_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    all_day: Mapped[bool] = mapped_column(Boolean, default=False)

    # Organization
    course_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    department_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("cms_departments.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Author tracking (SQL IDs)
    created_by_teacher_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_by_admin_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    department: Mapped[Optional["Department"]] = relationship(
        "Department", back_populates="calendar_events"
    )

    __table_args__ = (
        Index("ix_cms_calendar_events_start_date", "start_date"),
        Index("ix_cms_calendar_events_end_date", "end_date"),
        Index("ix_cms_calendar_events_event_type", "event_type"),
    )
