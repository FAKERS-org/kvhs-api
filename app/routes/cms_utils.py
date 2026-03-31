from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from app.core.dependencies import get_current_user, require_admin
from app.models import ContentTag, Department
from app.schemas import (
    ContentTagCreate,
    ContentTagRead,
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
)

router = APIRouter(prefix="/cms", tags=["CMS Utilities"])


# ==================== Department Routes ====================


@router.post(
    "/departments", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED
)
async def create_department(
    dept_data: DepartmentCreate,
    current_user: dict = Depends(require_admin),
):
    """Create a new department (admin only)."""
    # Check if department name already exists
    existing = await Department.find_one(Department.name == dept_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department name already exists",
        )

    new_dept = Department(name=dept_data.name, description=dept_data.description)
    await new_dept.insert()
    return new_dept


@router.get("/departments", response_model=list[DepartmentRead])
async def list_departments(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
):
    """List all departments."""
    departments = await Department.find_all().skip(skip).limit(limit).to_list()
    return departments


@router.get("/departments/{dept_id}", response_model=DepartmentRead)
async def get_department(
    dept_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific department."""
    dept = await Department.get(dept_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )
    return dept


@router.put("/departments/{dept_id}", response_model=DepartmentRead)
async def update_department(
    dept_id: str,
    dept_data: DepartmentUpdate,
    current_user: dict = Depends(require_admin),
):
    """Update a department (admin only)."""
    dept = await Department.get(dept_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )

    update_data = dept_data.model_dump(exclude_unset=True)

    # Check name uniqueness if being updated
    if "name" in update_data and update_data["name"] != dept.name:
        existing = await Department.find_one(Department.name == update_data["name"])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department name already exists",
            )

    for key, value in update_data.items():
        setattr(dept, key, value)

    await dept.save()
    return dept


@router.delete("/departments/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    dept_id: str,
    current_user: dict = Depends(require_admin),
):
    """Delete a department (admin only)."""
    dept = await Department.get(dept_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )

    await dept.delete()
    return None


# ==================== Content Tag Routes ====================


@router.post(
    "/tags", response_model=ContentTagRead, status_code=status.HTTP_201_CREATED
)
async def create_tag(
    tag_data: ContentTagCreate,
    current_user: dict = Depends(require_admin),
):
    """Create a new content tag (admin only)."""
    # Check if tag name already exists
    existing = await ContentTag.find_one(ContentTag.name == tag_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Tag name already exists"
        )

    new_tag = ContentTag(name=tag_data.name)
    await new_tag.insert()
    return new_tag


@router.get("/tags", response_model=list[ContentTagRead])
async def list_tags(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
):
    """List all tags."""
    tags = await ContentTag.find_all().skip(skip).limit(limit).to_list()
    return tags


@router.get("/tags/{tag_id}", response_model=ContentTagRead)
async def get_tag(
    tag_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific tag."""
    tag = await ContentTag.get(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return tag


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: str,
    current_user: dict = Depends(require_admin),
):
    """Delete a tag (admin only)."""
    tag = await ContentTag.get(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )

    await tag.delete()
    return None
