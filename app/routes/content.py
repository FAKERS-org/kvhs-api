from datetime import UTC, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from beanie.operators import In

from app.core.constants import PublishStatus, UserRole
from app.core.dependencies import get_current_user, get_db, require_teacher_or_admin
from app.models import (
    Content,
    ContentTag,
)
from app.schemas import ContentCreate, ContentRead, ContentUpdate

router = APIRouter(prefix="/content", tags=["Content Management"])


@router.post("/", response_model=ContentRead, status_code=status.HTTP_201_CREATED)
async def create_content(
    content_data: ContentCreate,
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Create new content (teachers can create course-related content, admins can create any content)."""
    # Check if slug already exists
    existing = await Content.find_one(Content.slug == content_data.slug)
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

    # Handle tags
    if content_data.tag_ids:
        new_content.tag_ids = content_data.tag_ids

    await new_content.insert()
    
    # Populate tags for response
    if new_content.tag_ids:
        tags = await ContentTag.find(In(ContentTag.id, new_content.tag_ids)).to_list()
        new_content.tags = tags
    else:
        new_content.tags = []
        
    return new_content


@router.get("/", response_model=list[ContentRead])
async def list_content(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    content_type: Optional[str] = None,
    department_id: Optional[str] = None,
    course_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
):
    """List content with optional filters. Students can only see published content."""
    query = Content.find_all()

    # Students can only see published content
    if current_user["role"] == UserRole.STUDENT.value:
        query = query.find(Content.status == PublishStatus.PUBLISHED.value)

    # Apply filters
    if status:
        query = query.find(Content.status == status)
    if content_type:
        query = query.find(Content.content_type == content_type)
    if department_id:
        query = query.find(Content.department_id == department_id)
    if course_id:
        query = query.find(Content.course_id == course_id)

    contents = await query.skip(skip).limit(limit).to_list()
    
    # Optionally populate tags for each content (could be optimized)
    for content in contents:
        if content.tag_ids:
            content.tags = await ContentTag.find(In(ContentTag.id, content.tag_ids)).to_list()
        else:
            content.tags = []
            
    return contents


@router.get("/{content_id}", response_model=ContentRead)
async def get_content(
    content_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific content by ID."""
    content = await Content.get(content_id)

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

    # Populate tags
    if content.tag_ids:
        content.tags = await ContentTag.find(In(ContentTag.id, content.tag_ids)).to_list()
    else:
        content.tags = []

    return content


@router.put("/{content_id}", response_model=ContentRead)
async def update_content(
    content_id: str,
    content_data: ContentUpdate,
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Update content. Teachers can only update their own content, admins can update any."""
    content = await Content.get(content_id)

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
        existing = await Content.find_one(Content.slug == update_data["slug"])
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
        content.tag_ids = tag_ids

    # Update other fields
    for key, value in update_data.items():
        setattr(content, key, value)

    content.updated_at = datetime.now(UTC)
    await content.save()
    
    # Populate tags
    if content.tag_ids:
        content.tags = await ContentTag.find(In(ContentTag.id, content.tag_ids)).to_list()
    else:
        content.tags = []
        
    return content


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: str,
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Delete content. Teachers can only delete their own content, admins can delete any."""
    content = await Content.get(content_id)

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

    await content.delete()
    return None


@router.post("/{content_id}/publish", response_model=ContentRead)
async def publish_content(
    content_id: str,
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Publish content."""
    content = await Content.get(content_id)

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

    await content.save()
    
    # Populate tags
    if content.tag_ids:
        content.tags = await ContentTag.find(In(ContentTag.id, content.tag_ids)).to_list()
    else:
        content.tags = []
        
    return content


@router.post("/{content_id}/unpublish", response_model=ContentRead)
async def unpublish_content(
    content_id: str,
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Unpublish content."""
    content = await Content.get(content_id)

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

    await content.save()
    
    # Populate tags
    if content.tag_ids:
        content.tags = await ContentTag.find(In(ContentTag.id, content.tag_ids)).to_list()
    else:
        content.tags = []
        
    return content
