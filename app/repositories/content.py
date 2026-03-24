"""
Content repository with CMS-specific operations.
"""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Content, ContentTag, ContentTagAssociation
from app.repositories.base import BaseRepository


class ContentRepository(BaseRepository[Content]):
    """Repository for Content model."""

    def __init__(self, db: Session):
        super().__init__(Content, db)

    def get_by_slug(self, slug: str) -> Content | None:
        """Get content by slug."""
        return self.get_by_field("slug", slug)

    def get_by_status(
        self, status: str, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by status."""
        return self.get_multi_by_field("status", status, skip, limit)

    def get_by_type(
        self, content_type: str, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by type."""
        return self.get_multi_by_field("content_type", content_type, skip, limit)

    def get_by_department(
        self, department_id: int, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by department."""
        return self.get_multi_by_field("department_id", department_id, skip, limit)

    def get_by_course(
        self, course_id: int, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by course."""
        return self.get_multi_by_field("course_id", course_id, skip, limit)

    def get_by_author_teacher(
        self, teacher_id: int, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by teacher author."""
        return self.get_multi_by_field("author_teacher_id", teacher_id, skip, limit)

    def search(
        self,
        query: str,
        content_type: str | None = None,
        department_id: int | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[Content]:
        """Search content with filters."""
        db_query = self.db.query(Content)

        # Text search
        if query:
            search_term = f"%{query}%"
            db_query = db_query.filter(
                or_(Content.title.ilike(search_term), Content.body.ilike(search_term))
            )

        # Filters
        if content_type:
            db_query = db_query.filter(Content.content_type == content_type)
        if department_id:
            db_query = db_query.filter(Content.department_id == department_id)
        if status:
            db_query = db_query.filter(Content.status == status)

        return db_query.limit(limit).all()

    def add_tags(self, content_id: int, tag_ids: list[int]) -> None:
        """Add tags to content."""
        # Remove existing associations
        self.db.query(ContentTagAssociation).filter(
            ContentTagAssociation.content_id == content_id
        ).delete()

        # Add new associations
        for tag_id in tag_ids:
            association = ContentTagAssociation(content_id=content_id, tag_id=tag_id)
            self.db.add(association)

        self.db.commit()

    def get_published(self, skip: int = 0, limit: int = 100) -> list[Content]:
        """Get all published content."""
        return (
            self.db.query(Content)
            .filter(Content.status == "published")
            .offset(skip)
            .limit(limit)
            .all()
        )
