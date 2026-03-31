"""
Content management routes.
Handles CRUD operations for CMS content.
"""

from datetime import UTC, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.constants import PublishStatus, UserRole
from app.core.dependencies import get_current_user, get_db, require_teacher_or_admin
from app.models.cms import Content, ContentTag
from app.schemas.cms import ContentCreate, ContentRead, ContentUpdate

router = APIRouter(prefix="/content", tags=["Content Management"])


@router.post("/", response_model=ContentRead, status_code=status.HTTP_201_CREATED)
async def create_content(
    content_data: ContentCreate,
    current_user: dict = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Create new content (teachers can create course-related content, admins can create any content)."""
    # Check if slug already exists
    existing = db.query(Content).filter(Content.slug == content_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists"
        )

    # Prepare data
    content_dict = content_data.model_dump(exclude={"tag_ids"})

    # Create content instance
    new_content = Content(**content_dict)

    # Set author based on user role
    if current_user["role"] == UserRole.TEACHER.value:
        new_content.author_teacher_id = current_user["id"]
    else:
        new_content.author_admin_id = current_user["id"]

    # Set published_at if status is published
    if content_data.status == PublishStatus.PUBLISHED.value:
        new_content.published_at = datetime.now(UTC)

    # Add tags relationship
    if content_data.tag_ids:
        tags = db.query(ContentTag).filter(ContentTag.id.in_(content_data.tag_ids)).all()
        new_content.tags = tags

    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    return new_content


@router.get("/", response_model=list[ContentRead])
async def list_content(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    content_type: Optional[str] = None,
    department_id: Optional[int] = None,
    course_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List content with optional filters. Students can only see published content."""
    query = db.query(Content).options(joinedload(Content.tags))

    # Students can only see published content
    if current_user["role"] == UserRole.STUDENT.value:
        query = query.filter(Content.status == PublishStatus.PUBLISHED.value)

    # Apply filters
    if status:
        query = query.filter(Content.status == status)
    if content_type:
        query = query.filter(Content.content_type == content_type)
    if department_id:
        query = query.filter(Content.department_id == department_id)
    if course_id:
        query = query.filter(Content.course_id == course_id)

    contents = query.offset(skip).limit(limit).all()
    return contents


@router.get("/{content_id}", response_model=ContentRead)
async def get_content(
    content_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific content by ID."""
    content = db.query(Content).options(joinedload(Content.tags)).filter(
        Content.id == content_id
    ).first()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    # Students can only view published content
    if (
        current_user["role"] == UserRole.STUDENT.value
        and content.status != PublishStatus.PUBLISHED.value
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to unpublished content",
        )

    return content


@router.put("/{content_id}", response_model=ContentRead)
async def update_content(
    content_id: int,
    content_data: ContentUpdate,
    current_user: dict = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Update content. Teachers can only update their own content, admins can update any."""
    content = db.query(Content).filter(Content.id == content_id).first()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    # Teachers can only update their own content
    if current_user["role"] == UserRole.TEACHER.value:
        if content.author_teacher_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this content",
            )

    # Update fields
    update_data = content_data.model_dump(exclude_unset=True)

    # Check slug uniqueness if being updated
    if "slug" in update_data and update_data["slug"] != content.slug:
        existing = db.query(Content).filter(Content.slug == update_data["slug"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists"
            )

    # Update published_at if status changes to published
    if (
        "status" in update_data
        and update_data["status"] == PublishStatus.PUBLISHED.value
    ):
        if content.status != PublishStatus.PUBLISHED.value:
            content.published_at = datetime.now(UTC)

    # Update tags if provided
    tag_ids = update_data.pop("tag_ids", None)
    if tag_ids is not None:
        tags = db.query(ContentTag).filter(ContentTag.id.in_(tag_ids)).all()
        content.tags = tags

    # Update other fields
    for key, value in update_data.items():
        setattr(content, key, value)

    content.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(content)
    return content


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: int,
    current_user: dict = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Delete content. Teachers can only delete their own content, admins can delete any."""
    content = db.query(Content).filter(Content.id == content_id).first()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    # Teachers can only delete their own content
    if current_user["role"] == UserRole.TEACHER.value:
        if content.author_teacher_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this content",
            )

    db.delete(content)
    db.commit()
    return None


@router.post("/{content_id}/publish", response_model=ContentRead)
async def publish_content(
    content_id: int,
    current_user: dict = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Publish content."""
    content = db.query(Content).options(joinedload(Content.tags)).filter(
        Content.id == content_id
    ).first()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    # Teachers can only publish their own content
    if current_user["role"] == UserRole.TEACHER.value:
        if content.author_teacher_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to publish this content",
            )

    content.status = PublishStatus.PUBLISHED.value
    content.published_at = datetime.now(UTC)
    content.updated_at = datetime.now(UTC)

    db.commit()
    db.refresh(content)
    return content


@router.post("/{content_id}/unpublish", response_model=ContentRead)
async def unpublish_content(
    content_id: int,
    current_user: dict = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Unpublish content."""
    content = db.query(Content).options(joinedload(Content.tags)).filter(
        Content.id == content_id
    ).first()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    # Teachers can only unpublish their own content
    if current_user["role"] == UserRole.TEACHER.value:
        if content.author_teacher_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to unpublish this content",
            )

    content.status = PublishStatus.UNPUBLISHED.value
    content.updated_at = datetime.now(UTC)

    db.commit()
    db.refresh(content)
    return content
