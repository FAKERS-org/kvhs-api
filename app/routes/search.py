from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from beanie.operators import In

from app.core.constants import PublishStatus, UserRole
from app.core.dependencies import get_current_user
from app.models import (
    Content,
    ContentTag,
)
from app.schemas import ContentRead, SearchRequest

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/", response_model=list[ContentRead])
async def search_content(
    search_params: SearchRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Search for content by text, tags, categories, and department.
    Students can only search published content.
    """
    filters = {}

    # Students can only search published content
    if current_user["role"] == UserRole.STUDENT.value:
        filters["status"] = PublishStatus.PUBLISHED.value
    elif search_params.status:
        filters["status"] = search_params.status

    # Text search (search in title and body)
    if search_params.query:
        filters["$or"] = [
            {"title": {"$regex": search_params.query, "$options": "i"}},
            {"body": {"$regex": search_params.query, "$options": "i"}}
        ]

    # Filter by content type
    if search_params.content_type:
        filters["content_type"] = search_params.content_type

    # Filter by department
    if search_params.department_id:
        filters["department_id"] = search_params.department_id

    # Filter by tags
    if search_params.tags:
        # Find tag IDs from tag names
        tags = await ContentTag.find(In(ContentTag.name, search_params.tags)).to_list()
        tag_ids = [str(tag.id) for tag in tags]

        if tag_ids:
            # Find content that has any of these tags
            filters["tag_ids"] = {"$in": tag_ids}
        else:
            # No content with these tags
            return []

    results = await Content.find(filters).limit(100).to_list()
    
    # Populate tags for each content
    for content in results:
        if content.tag_ids:
            content.tags = await ContentTag.find(In(ContentTag.id, content.tag_ids)).to_list()
        else:
            content.tags = []
            
    return results


@router.get("/", response_model=list[ContentRead])
async def search_content_get(
    q: str,
    content_type: Optional[str] = None,
    department_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Search for content using GET method (for simpler queries).
    Students can only search published content.
    """
    filters = {}

    # Students can only search published content
    if current_user["role"] == UserRole.STUDENT.value:
        filters["status"] = PublishStatus.PUBLISHED.value
    elif status:
        filters["status"] = status

    # Text search
    if q:
        filters["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"body": {"$regex": q, "$options": "i"}}
        ]

    # Filter by content type
    if content_type:
        filters["content_type"] = content_type

    # Filter by department
    if department_id:
        filters["department_id"] = department_id

    results = await Content.find(filters).limit(100).to_list()
    
    # Populate tags for each content
    for content in results:
        if content.tag_ids:
            content.tags = await ContentTag.find(In(ContentTag.id, content.tag_ids)).to_list()
        else:
            content.tags = []
            
    return results
