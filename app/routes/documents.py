"""
Document management routes.
Handles file uploads to MinIO and metadata in PostgreSQL.
"""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.constants import UserRole
from app.core.dependencies import get_current_user, get_db, require_teacher_or_admin
from app.models.cms import CMSDocument
from app.schemas.cms import DocumentRead, DocumentUpdate
from app.utils.minio_client import (
    upload_file_to_minio,
    stream_file_from_minio,
    delete_file_from_minio,
)

router = APIRouter(prefix="/documents", tags=["Document Management"])


def generate_unique_object_name(filename: str) -> str:
    """Generate a unique object name for MinIO storage."""
    unique_id = uuid.uuid4().hex
    timestamp = datetime.now().strftime("%Y%m%d")
    return f"{timestamp}/{unique_id}_{filename}"


@router.post("/", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def create_document(
    title: str = Form(...),
    content_id: Optional[int] = Form(None),
    course_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Upload a new document to MinIO and save metadata to PostgreSQL."""
    # Generate unique object name for MinIO
    object_name = generate_unique_object_name(file.filename or "unnamed")
    
    # Upload to MinIO
    minio_object_name, file_size = await upload_file_to_minio(file, object_name)

    # Create document record
    new_doc = CMSDocument(
        title=title,
        filename=file.filename or "unnamed",
        minio_object_name=minio_object_name,
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream",
        content_id=content_id,
        course_id=course_id,
    )

    # Set uploader based on user role
    if current_user["role"] == UserRole.TEACHER.value:
        new_doc.uploaded_by_teacher_id = current_user["id"]
    else:
        new_doc.uploaded_by_admin_id = current_user["id"]

    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


@router.get("/", response_model=list[DocumentRead])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    content_id: Optional[int] = None,
    course_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List documents with optional filters."""
    query = db.query(CMSDocument)

    if content_id:
        query = query.filter(CMSDocument.content_id == content_id)
    if course_id:
        query = query.filter(CMSDocument.course_id == course_id)

    documents = query.offset(skip).limit(limit).all()
    return documents


@router.get("/{doc_id}", response_model=DocumentRead)
async def get_document(
    doc_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific document by ID."""
    doc = db.query(CMSDocument).filter(CMSDocument.id == doc_id).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    return doc


@router.get("/{doc_id}/download")
async def download_document(
    doc_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download a document file from MinIO."""
    doc = db.query(CMSDocument).filter(CMSDocument.id == doc_id).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    return StreamingResponse(
        stream_file_from_minio(doc.minio_object_name),
        media_type=doc.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{doc.filename}"'},
    )


@router.put("/{doc_id}", response_model=DocumentRead)
async def update_document(
    doc_id: int,
    doc_data: DocumentUpdate,
    current_user: dict = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Update document metadata."""
    doc = db.query(CMSDocument).filter(CMSDocument.id == doc_id).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # Teachers can only update their own documents
    if current_user["role"] == UserRole.TEACHER.value:
        if doc.uploaded_by_teacher_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this document",
            )

    update_data = doc_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(doc, key, value)

    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    current_user: dict = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db),
):
    """Delete a document."""
    doc = db.query(CMSDocument).filter(CMSDocument.id == doc_id).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # Teachers can only delete their own documents
    if current_user["role"] == UserRole.TEACHER.value:
        if doc.uploaded_by_teacher_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this document",
            )

    # Delete from MinIO
    if doc.minio_object_name:
        await delete_file_from_minio(doc.minio_object_name)

    # Delete from database
    db.delete(doc)
    db.commit()
    return None
