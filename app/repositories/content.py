"""
Content repository with CMS-specific operations using Beanie (MongoDB).
"""

from typing import Optional
from beanie.operators import RegEx

from app.models import Content, ContentTag
from app.core.constants import PublishStatus


class ContentRepository:
    """Repository for Content model (MongoDB)."""

    async def get(self, id: str) -> Optional[Content]:
        """Get a single record by ID."""
        return await Content.get(id)

    async def get_by_slug(self, slug: str) -> Optional[Content]:
        """Get content by slug."""
        return await Content.find_one(Content.slug == slug)

    async def get_multi(self, skip: int = 0, limit: int = 100) -> list[Content]:
        """Get multiple records with pagination."""
        return await Content.find_all().skip(skip).limit(limit).to_list()

    async def get_by_status(
        self, status: str, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by status."""
        return await Content.find(Content.status == status).skip(skip).limit(limit).to_list()

    async def get_by_type(
        self, content_type: str, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by type."""
        return await Content.find(Content.content_type == content_type).skip(skip).limit(limit).to_list()

    async def get_by_department(
        self, department_id: str, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by department."""
        return await Content.find(Content.department_id == department_id).skip(skip).limit(limit).to_list()

    async def get_by_course(
        self, course_id: int, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by course."""
        return await Content.find(Content.course_id == course_id).skip(skip).limit(limit).to_list()

    async def get_by_author_teacher(
        self, teacher_id: int, skip: int = 0, limit: int = 100
    ) -> list[Content]:
        """Get content by teacher author."""
        return await Content.find(Content.author_teacher_id == teacher_id).skip(skip).limit(limit).to_list()

    async def search(
        self,
        query: str,
        content_type: Optional[str] = None,
        department_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> list[Content]:
        """Search content with filters."""
        filters = {}
        if query:
            # Simple regex search for title or body
            filters["$or"] = [
                {"title": {"$regex": query, "$options": "i"}},
                {"body": {"$regex": query, "$options": "i"}}
            ]
        
        if content_type:
            filters["content_type"] = content_type
        if department_id:
            filters["department_id"] = department_id
        if status:
            filters["status"] = status

        return await Content.find(filters).limit(limit).to_list()

    async def create(self, obj_in: dict) -> Content:
        """Create a new record."""
        new_obj = Content(**obj_in)
        return await new_obj.insert()

    async def update(self, db_obj: Content, obj_in: dict) -> Content:
        """Update an existing record."""
        update_data = obj_in.copy()
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db_obj.save()
        return db_obj

    async def delete(self, db_obj: Content) -> None:
        """Delete a record."""
        await db_obj.delete()

    async def get_published(self, skip: int = 0, limit: int = 100) -> list[Content]:
        """Get all published content."""
        return await Content.find(Content.status == PublishStatus.PUBLISHED.value).skip(skip).limit(limit).to_list()
