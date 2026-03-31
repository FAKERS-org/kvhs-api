"""
Models package - exports all database models.

Note: CMS models use SQLAlchemy (PostgreSQL).
"""

from app.models.base import Base, TimestampMixin
from app.models.user import Admin, Student, Teacher
from app.models.academic import AssignmentScore, Attendance, Course, Enrollment
# CMS models - SQLAlchemy for PostgreSQL
from app.models.cms import (
    CalendarEvent,
    Content,
    ContentTag,
    Department,
    CMSDocument as Document,
)

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    # Users
    "Student",
    "Teacher",
    "Admin",
    # Academic
    "Course",
    "Enrollment",
    "Attendance",
    "AssignmentScore",
    # CMS (SQLAlchemy - PostgreSQL)
    "Content",
    "Document",
    "CalendarEvent",
    "Department",
    "ContentTag",
]
