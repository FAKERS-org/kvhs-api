from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.constants import PublishStatus, UserRole
from app.core.dependencies import get_current_user, get_db
from app.models import (
    Content,
    ContentTag,
    ContentTagAssociation,
)
from app.schemas import ContentRead, SearchRequest

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/", response_model=list[ContentRead])
def search_content(
    search_params: SearchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Search for content by text, tags, categories, and department.
    Students can only search published content.
    """
    query = db.query(Content)

    # Students can only search published content
    if current_user["role"] == UserRole.STUDENT.value:
        query = query.filter(Content.status == PublishStatus.PUBLISHED.value)

    # Text search (search in title and body)
    if search_params.query:
        search_term = f"%{search_params.query}%"
        query = query.filter(
            or_(Content.title.ilike(search_term), Content.body.ilike(search_term))
        )

    # Filter by content type
    if search_params.content_type:
        query = query.filter(Content.content_type == search_params.content_type)

    # Filter by department
    if search_params.department_id:
        query = query.filter(Content.department_id == search_params.department_id)

    # Filter by status (only for non-students)
    if search_params.status and current_user["role"] != UserRole.STUDENT.value:
        query = query.filter(Content.status == search_params.status)

    # Filter by tags
    if search_params.tags:
        # Get tag IDs from tag names
        tag_ids = (
            db.query(ContentTag.id)
            .filter(ContentTag.name.in_(search_params.tags))
            .all()
        )
        tag_ids = [tag_id[0] for tag_id in tag_ids]

        if tag_ids:
            # Find content that has any of these tags
            content_ids = (
                db.query(ContentTagAssociation.content_id)
                .filter(ContentTagAssociation.tag_id.in_(tag_ids))
                .distinct()
                .all()
            )
            content_ids = [cid[0] for cid in content_ids]

            if content_ids:
                query = query.filter(Content.id.in_(content_ids))
            else:
                # No content with these tags
                return []

    results = query.limit(100).all()
    return results


@router.get("/", response_model=list[ContentRead])
def search_content_get(
    q: str,
    content_type: str | None = None,
    department_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Search for content using GET method (for simpler queries).
    Students can only search published content.
    """
    query = db.query(Content)

    # Students can only search published content
    if current_user["role"] == UserRole.STUDENT.value:
        query = query.filter(Content.status == PublishStatus.PUBLISHED.value)

    # Text search
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(Content.title.ilike(search_term), Content.body.ilike(search_term))
        )

    # Filter by content type
    if content_type:
        query = query.filter(Content.content_type == content_type)

    # Filter by department
    if department_id:
        query = query.filter(Content.department_id == department_id)

    # Filter by status (only for non-students)
    if status and current_user["role"] != UserRole.STUDENT.value:
        query = query.filter(Content.status == status)

    results = query.limit(100).all()
    return results
