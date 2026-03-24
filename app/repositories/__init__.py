"""
Repositories package - exports all repository classes.
"""

from app.repositories.base import BaseRepository
from app.repositories.user import AdminRepository, StudentRepository, TeacherRepository
from app.repositories.content import ContentRepository

__all__ = [
    "BaseRepository",
    "StudentRepository",
    "TeacherRepository",
    "AdminRepository",
    "ContentRepository",
]
