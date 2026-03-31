"""
Content repository with CMS-specific operations (SQLAlchemy version).
"""

from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.cms import Content, ContentTag
from app.core.constants import PublishStatus


class ContentRepository:
    """Repository for Content model (PostgreSQL)."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[Content]:
        """Get a single record by ID."""
        return self.db.query(Content).filter(Content.id == id).first()

    def get_by_slug(self, slug: str) -> Optional[Content]:
        """Get content by slug."""
        return self.db.query(Content).filter(Content.slug == slug).first()

    def get_multi(self, skip: int = 0, limit: int = 100) -> list[Content]:
        """Get multiple records with pagination."""
        return self.db.query(Content).offset(skip).limit(limit).all()

    def get_by_status(
        self, status: str, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by status."""
        return self.db.query(Content).filter(Content.status == status).offset(skip).limit(limit).all()

    def get_by_type(
        self, content_type: str, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by type."""
        return self.db.query(Content).filter(Content.content_type == content_type).offset(skip).limit(limit).all()

    def get_by_department(
        self, department_id: int, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by department."""
        return self.db.query(Content).filter(Content.department_id == department_id).offset(skip).limit(limit).all()

    def get_by_course(
        self, course_id: int, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by course."""
        return self.db.query(Content).filter(Content.course_id == course_id).offset(skip).limit(limit).all()

    def get_by_author_teacher(
        self, teacher_id: int, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by teacher author."""
        return self.db.query(Content).filter(Content.author_teacher_id == teacher_id).offset(skip).limit(limit).all()

    def search(
        self,
        query: str,
        content_type: Optional[str] = None,
        department_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> list[Content]:
        """Search content with filters."""
        db_query = self.db.query(Content)
        
        if query:
            # ILIKE search for title or body (PostgreSQL)
            search_term = f"%{query}%"
            db_query = db_query.filter(
                (Content.title.ilike(search_term)) |
                (Content.body.ilike(search_term))
            )

        if content_type:
            db_query = db_query.filter(Content.content_type == content_type)
        if department_id:
            db_query = db_query.filter(Content.department_id == department_id)
        if status:
            db_query = db_query.filter(Content.status == status)

        return db_query.limit(limit).all()

    def create(self, obj_in: dict) -> Content:
        """Create a new record."""
        new_obj = Content(**obj_in)
        self.db.add(new_obj)
        self.db.commit()
        self.db.refresh(new_obj)
        return new_obj

    def update(self, db_obj: Content, obj_in: dict) -> Content:
        """Update an existing record."""
        update_data = obj_in.copy()
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: Content) -> None:
        """Delete a record."""
        self.db.delete(db_obj)
        self.db.commit()

    def get_published(self, skip: int = 0, limit: int = 100) -> list[Content]:
        """Get all published content."""
        return self.db.query(Content).filter(
            Content.status == PublishStatus.PUBLISHED.value
        ).offset(skip).limit(limit).all()
