from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.constants import UserRole
from app.core.dependencies import get_current_user, get_db, require_teacher_or_admin
from app.models import Document
from app.schemas import DocumentRead, DocumentUpdate
from app.utils.cloudinary import upload_file_to_cloudinary, delete_file_from_cloudinary

router = APIRouter(prefix="/documents", tags=["Document Management"])


@router.post("/", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def create_document(
    title: str = Form(...),
    content_id: int | None = Form(None),
    course_id: int | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Upload a new document to Cloudinary and save metadata."""
    # Upload to Cloudinary
    cloudinary_result = await upload_file_to_cloudinary(file)
    
    if not cloudinary_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to storage"
        )

    new_doc = Document(
        title=title,
        filename=file.filename,
        file_path=cloudinary_result.get("secure_url"),
        cloudinary_public_id=cloudinary_result.get("public_id"),
        file_size=cloudinary_result.get("bytes"),
        mime_type=file.content_type,
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
def list_documents(
    skip: int = 0,
    limit: int = 100,
    content_id: int | None = None,
    course_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List documents with optional filters."""
    query = db.query(Document)

    if content_id:
        query = query.filter(Document.content_id == content_id)
    if course_id:
        query = query.filter(Document.course_id == course_id)

    documents = query.offset(skip).limit(limit).all()
    return documents


@router.get("/{doc_id}", response_model=DocumentRead)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific document by ID."""
    doc = db.query(Document).filter(Document.id == doc_id).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    return doc


@router.put("/{doc_id}", response_model=DocumentRead)
def update_document(
    doc_id: int,
    doc_data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Update document metadata."""
    doc = db.query(Document).filter(Document.id == doc_id).first()

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
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_or_admin),
):
    """Delete a document."""
    doc = db.query(Document).filter(Document.id == doc_id).first()

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

    # Delete from Cloudinary if public_id exists
    if doc.cloudinary_public_id:
        delete_file_from_cloudinary(doc.cloudinary_public_id)

    db.delete(doc)
    db.commit()
    return None
