from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.constants import PublishStatus, UserRole
from app.core.dependencies import get_current_user, get_db, require_teacher_or_admin
from app.models import (
    Content,
    ContentTag,
    ContentTagAssociation,
)
from app.schemas import ContentCreate, ContentRead, ContentUpdate

router = APIRouter(prefix="/content", tags=["Content Management"])


@router.post("/", response_model=ContentRead, status_code=status.HTTP_201_CREATED)
def create_content(
    content_data: ContentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Create new content (teachers can create course-related content, admins can create any content)."""
    # Check if slug already exists
    existing = db.query(Content).filter(Content.slug == content_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists"
        )

    # Create content
    new_content = Content(
        title=content_data.title,
        slug=content_data.slug,
        content_type=content_data.content_type,
        body=content_data.body,
        template=content_data.template,
        status=content_data.status,
        department_id=content_data.department_id,
        course_id=content_data.course_id,
        parent_id=content_data.parent_id,
    )

    # Set author based on user role
    if current_user["role"] == UserRole.TEACHER.value:
        new_content.author_teacher_id = current_user["id"]
    else:
        new_content.author_admin_id = current_user["id"]

    # Set published_at if status is published
    if content_data.status == PublishStatus.PUBLISHED.value:
        new_content.published_at = datetime.now(UTC)

    db.add(new_content)
    db.commit()

    # Add tags if provided
    if content_data.tag_ids:
        for tag_id in content_data.tag_ids:
            tag = db.query(ContentTag).filter(ContentTag.id == tag_id).first()
            if tag:
                association = ContentTagAssociation(
                    content_id=new_content.id, tag_id=tag_id
                )
                db.add(association)
        db.commit()

    db.refresh(new_content)
    return new_content


@router.get("/", response_model=list[ContentRead])
def list_content(
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    content_type: str | None = None,
    department_id: int | None = None,
    course_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List content with optional filters. Students can only see published content."""
    query = db.query(Content)

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
def get_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific content by ID."""
    content = db.query(Content).filter(Content.id == content_id).first()

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
def update_content(
    content_id: int,
    content_data: ContentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_or_admin),
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

    # Handle tag updates separately
    tag_ids = update_data.pop("tag_ids", None)

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

    for key, value in update_data.items():
        setattr(content, key, value)

    # Update tags if provided
    if tag_ids is not None:
        # Remove existing tag associations
        db.query(ContentTagAssociation).filter(
            ContentTagAssociation.content_id == content_id
        ).delete()

        # Add new associations
        for tag_id in tag_ids:
            tag = db.query(ContentTag).filter(ContentTag.id == tag_id).first()
            if tag:
                association = ContentTagAssociation(
                    content_id=content_id, tag_id=tag_id
                )
                db.add(association)

    db.commit()
    db.refresh(content)
    return content


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_or_admin),
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
def publish_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Publish content."""
    content = db.query(Content).filter(Content.id == content_id).first()

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

    db.commit()
    db.refresh(content)
    return content


@router.post("/{content_id}/unpublish", response_model=ContentRead)
def unpublish_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Unpublish content."""
    content = db.query(Content).filter(Content.id == content_id).first()

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

    db.commit()
    db.refresh(content)
    return content
