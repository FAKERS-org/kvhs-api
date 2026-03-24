"""
Content service with CMS business logic.
"""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.constants import ErrorMessages, PublishStatus, UserRole
from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError
from app.models import Content
from app.repositories.content import ContentRepository
from app.schemas import ContentCreate, ContentUpdate


class ContentService:
    """Content management service."""

    def __init__(self, db: Session):
        self.db = db
        self.content_repo = ContentRepository(db)

    def create_content(
        self, data: ContentCreate, user_id: int, user_role: str
    ) -> Content:
        """Create new content."""
        # Check if slug exists
        if self.content_repo.get_by_slug(data.slug):
            raise ConflictError(ErrorMessages.SLUG_EXISTS)

        # Prepare content data
        content_data = {
            "title": data.title,
            "slug": data.slug,
            "content_type": data.content_type,
            "body": data.body,
            "template": data.template,
            "status": data.status,
            "department_id": data.department_id,
            "course_id": data.course_id,
            "parent_id": data.parent_id,
        }

        # Set author based on role
        if user_role == UserRole.TEACHER.value:
            content_data["author_teacher_id"] = user_id
        else:
            content_data["author_admin_id"] = user_id

        # Set published_at if status is published
        if data.status == PublishStatus.PUBLISHED.value:
            content_data["published_at"] = datetime.now(UTC)

        # Create content
        content = self.content_repo.create(content_data)

        # Add tags if provided
        if data.tag_ids:
            self.content_repo.add_tags(content.id, data.tag_ids)
            self.db.refresh(content)

        return content

    def get_content(self, content_id: int, user_role: str) -> Content:
        """Get content by ID with permission check."""
        content = self.content_repo.get(content_id)

        if not content:
            raise NotFoundError(ErrorMessages.CONTENT_NOT_FOUND)

        # Students can only view published content
        if (
            user_role == UserRole.STUDENT.value
            and content.status != PublishStatus.PUBLISHED.value
        ):
            raise AuthorizationError(ErrorMessages.ACCESS_DENIED_UNPUBLISHED)

        return content

    def list_content(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        content_type: str | None = None,
        department_id: int | None = None,
        course_id: int | None = None,
        user_role: str = None,
    ) -> list[Content]:
        """List content with filters."""
        # Students can only see published content
        if user_role == UserRole.STUDENT.value:
            return self.content_repo.get_published(skip, limit)

        # Apply filters for other users
        if status:
            return self.content_repo.get_by_status(status, skip, limit)
        elif content_type:
            return self.content_repo.get_by_type(content_type, skip, limit)
        elif department_id:
            return self.content_repo.get_by_department(department_id, skip, limit)
        elif course_id:
            return self.content_repo.get_by_course(course_id, skip, limit)

        return self.content_repo.get_multi(skip, limit)

    def update_content(
        self, content_id: int, data: ContentUpdate, user_id: int, user_role: str
    ) -> Content:
        """Update content with permission check."""
        content = self.content_repo.get(content_id)

        if not content:
            raise NotFoundError(ErrorMessages.CONTENT_NOT_FOUND)

        # Teachers can only update their own content
        if user_role == UserRole.TEACHER.value:
            if content.author_teacher_id != user_id:
                raise AuthorizationError(ErrorMessages.NOT_CONTENT_OWNER)

        # Prepare update data
        update_data = data.model_dump(exclude_unset=True)
        tag_ids = update_data.pop("tag_ids", None)

        # Check slug uniqueness if being updated
        if "slug" in update_data and update_data["slug"] != content.slug:
            if self.content_repo.get_by_slug(update_data["slug"]):
                raise ConflictError(ErrorMessages.SLUG_EXISTS)

        # Update published_at if status changes to published
        if (
            "status" in update_data
            and update_data["status"] == PublishStatus.PUBLISHED.value
        ):
            if content.status != PublishStatus.PUBLISHED.value:
                update_data["published_at"] = datetime.now(UTC)

        # Update content
        content = self.content_repo.update(content, update_data)

        # Update tags if provided
        if tag_ids is not None:
            self.content_repo.add_tags(content_id, tag_ids)
            self.db.refresh(content)

        return content

    def delete_content(self, content_id: int, user_id: int, user_role: str) -> None:
        """Delete content with permission check."""
        content = self.content_repo.get(content_id)

        if not content:
            raise NotFoundError(ErrorMessages.CONTENT_NOT_FOUND)

        # Teachers can only delete their own content
        if user_role == UserRole.TEACHER.value:
            if content.author_teacher_id != user_id:
                raise AuthorizationError(ErrorMessages.NOT_CONTENT_OWNER)

        self.content_repo.delete(content)

    def publish_content(self, content_id: int, user_id: int, user_role: str) -> Content:
        """Publish content."""
        content = self.content_repo.get(content_id)

        if not content:
            raise NotFoundError(ErrorMessages.CONTENT_NOT_FOUND)

        # Teachers can only publish their own content
        if user_role == UserRole.TEACHER.value:
            if content.author_teacher_id != user_id:
                raise AuthorizationError(ErrorMessages.NOT_CONTENT_OWNER)

        update_data = {
            "status": PublishStatus.PUBLISHED.value,
            "published_at": datetime.now(UTC),
        }

        return self.content_repo.update(content, update_data)

    def unpublish_content(
        self, content_id: int, user_id: int, user_role: str
    ) -> Content:
        """Unpublish content."""
        content = self.content_repo.get(content_id)

        if not content:
            raise NotFoundError(ErrorMessages.CONTENT_NOT_FOUND)

        # Teachers can only unpublish their own content
        if user_role == UserRole.TEACHER.value:
            if content.author_teacher_id != user_id:
                raise AuthorizationError(ErrorMessages.NOT_CONTENT_OWNER)

        update_data = {"status": PublishStatus.UNPUBLISHED.value}

        return self.content_repo.update(content, update_data)

    def search_content(
        self,
        query: str,
        content_type: str | None = None,
        department_id: int | None = None,
        status: str | None = None,
        user_role: str = None,
    ) -> list[Content]:
        """Search content with filters."""
        # Students can only search published content
        if user_role == UserRole.STUDENT.value:
            status = PublishStatus.PUBLISHED.value

        return self.content_repo.search(query, content_type, department_id, status)
