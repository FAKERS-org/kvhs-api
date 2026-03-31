from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional

from app.core.constants import UserRole
from app.core.dependencies import get_current_user, require_teacher_or_admin
from app.models import Document
from app.schemas import DocumentRead, DocumentUpdate
from app.utils.gridfs import (
    upload_file_to_gridfs,
    open_download_stream,
    delete_file_from_gridfs,
)

router = APIRouter(prefix="/documents", tags=["Document Management"])


@router.post("/", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def create_document(
    title: str = Form(...),
    content_id: Optional[str] = Form(None),
    course_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Upload a new document to GridFS and save metadata."""
    gridfs_id, file_size = await upload_file_to_gridfs(file)

    new_doc = Document(
        title=title,
        filename=file.filename,
        gridfs_id=gridfs_id,
        file_size=file_size,
        mime_type=file.content_type,
        content_id=content_id,
        course_id=course_id,
    )

    # Set uploader based on user role
    if current_user["role"] == UserRole.TEACHER.value:
        new_doc.uploaded_by_teacher_id = current_user["id"]
    else:
        new_doc.uploaded_by_admin_id = current_user["id"]

    await new_doc.insert()
    return new_doc


@router.get("/", response_model=list[DocumentRead])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    content_id: Optional[str] = None,
    course_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
):
    """List documents with optional filters."""
    query = Document.find_all()

    if content_id:
        query = query.find(Document.content_id == content_id)
    if course_id:
        query = query.find(Document.course_id == course_id)

    documents = await query.skip(skip).limit(limit).to_list()
    return documents


@router.get("/{doc_id}", response_model=DocumentRead)
async def get_document(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific document by ID."""
    doc = await Document.get(doc_id)

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    return doc


@router.get("/{doc_id}/download")
async def download_document(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Download a document file from GridFS."""
    doc = await Document.get(doc_id)

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    stream = await open_download_stream(doc.gridfs_id)

    async def file_iterator():
        while True:
            chunk = await stream.readchunk()
            if not chunk:
                break
            yield chunk

    return StreamingResponse(
        file_iterator(),
        media_type=doc.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{doc.filename}"'},
    )


@router.put("/{doc_id}", response_model=DocumentRead)
async def update_document(
    doc_id: str,
    doc_data: DocumentUpdate,
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Update document metadata."""
    doc = await Document.get(doc_id)

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

    await doc.save()
    return doc


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Delete a document."""
    doc = await Document.get(doc_id)

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

    if doc.gridfs_id:
        await delete_file_from_gridfs(doc.gridfs_id)

    await doc.delete()
    return None
