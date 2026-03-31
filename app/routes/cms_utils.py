"""
CMS utility routes.
Handles Department and ContentTag management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_admin
from app.models.cms import ContentTag, Department
from app.schemas.cms import (
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
    db: Session = Depends(get_db),
):
    """Create a new department (admin only)."""
    # Check if department name already exists
    existing = db.query(Department).filter(Department.name == dept_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department name already exists",
        )

    new_dept = Department(name=dept_data.name, description=dept_data.description)
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    return new_dept


@router.get("/departments", response_model=list[DepartmentRead])
async def list_departments(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all departments."""
    departments = db.query(Department).offset(skip).limit(limit).all()
    return departments


@router.get("/departments/{dept_id}", response_model=DepartmentRead)
async def get_department(
    dept_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific department."""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )
    return dept


@router.put("/departments/{dept_id}", response_model=DepartmentRead)
async def update_department(
    dept_id: int,
    dept_data: DepartmentUpdate,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update a department (admin only)."""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )

    update_data = dept_data.model_dump(exclude_unset=True)

    # Check name uniqueness if being updated
    if "name" in update_data and update_data["name"] != dept.name:
        existing = db.query(Department).filter(Department.name == update_data["name"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department name already exists",
            )

    for key, value in update_data.items():
        setattr(dept, key, value)

    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/departments/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    dept_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a department (admin only)."""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )

    db.delete(dept)
    db.commit()
    return None


# ==================== Content Tag Routes ====================


@router.post(
    "/tags", response_model=ContentTagRead, status_code=status.HTTP_201_CREATED
)
async def create_tag(
    tag_data: ContentTagCreate,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new content tag (admin only)."""
    # Check if tag name already exists
    existing = db.query(ContentTag).filter(ContentTag.name == tag_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Tag name already exists"
        )

    new_tag = ContentTag(name=tag_data.name)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag


@router.get("/tags", response_model=list[ContentTagRead])
async def list_tags(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all tags."""
    tags = db.query(ContentTag).offset(skip).limit(limit).all()
    return tags


@router.get("/tags/{tag_id}", response_model=ContentTagRead)
async def get_tag(
    tag_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific tag."""
    tag = db.query(ContentTag).filter(ContentTag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return tag


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a tag (admin only)."""
    tag = db.query(ContentTag).filter(ContentTag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )

    db.delete(tag)
    db.commit()
    return None
