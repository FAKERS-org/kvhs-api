"""
Search routes.
Handles content search functionality.
"""

from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.core.constants import PublishStatus, UserRole
from app.core.dependencies import get_current_user, get_db
from app.models.cms import Content, ContentTag
from app.schemas.cms import ContentRead
from app.schemas.search import SearchRequest

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/", response_model=list[ContentRead])
async def search_content(
    search_params: SearchRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search for content by text, tags, categories, and department.
    Students can only search published content.
    """
    query = db.query(Content).options(joinedload(Content.tags))

    # Students can only search published content
    if current_user["role"] == UserRole.STUDENT.value:
        query = query.filter(Content.status == PublishStatus.PUBLISHED.value)
    elif search_params.status:
        query = query.filter(Content.status == search_params.status)

    # Text search (search in title and body)
    if search_params.query:
        search_term = f"%{search_params.query}%"
        query = query.filter(
            or_(
                Content.title.ilike(search_term),
                Content.body.ilike(search_term),
            )
        )

    # Filter by content type
    if search_params.content_type:
        query = query.filter(Content.content_type == search_params.content_type)

    # Filter by department
    if search_params.department_id:
        query = query.filter(Content.department_id == search_params.department_id)

    # Filter by tags
    if search_params.tags:
        # Find tag IDs from tag names
        tags = db.query(ContentTag).filter(
            ContentTag.name.in_(search_params.tags)
        ).all()
        tag_ids = [tag.id for tag in tags]

        if tag_ids:
            # Find content that has any of these tags
            query = query.filter(Content.tags.any(ContentTag.id.in_(tag_ids)))
        else:
            # No content with these tags
            return []

    results = query.limit(100).all()
    return results


@router.get("/", response_model=list[ContentRead])
async def search_content_get(
    q: str,
    content_type: Optional[str] = None,
    department_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search for content using GET method (for simpler queries).
    Students can only search published content.
    """
    query = db.query(Content).options(joinedload(Content.tags))

    # Students can only search published content
    if current_user["role"] == UserRole.STUDENT.value:
        query = query.filter(Content.status == PublishStatus.PUBLISHED.value)
    elif status:
        query = query.filter(Content.status == status)

    # Text search
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Content.title.ilike(search_term),
                Content.body.ilike(search_term),
            )
        )

    # Filter by content type
    if content_type:
        query = query.filter(Content.content_type == content_type)

    # Filter by department
    if department_id:
        query = query.filter(Content.department_id == department_id)

    results = query.limit(100).all()
    return results
