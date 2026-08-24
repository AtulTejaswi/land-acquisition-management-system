from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import uuid
import os

from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.core.deps import require_role, get_current_user
from app.core.config import settings
from app.schemas.document import DocumentResponse, PaginatedDocuments

router = APIRouter(prefix="/documents", tags=["documents"])

# File upload validation constants
MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25MB
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    "application/geo+json",
    "application/json",
}
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".csv",
    ".geojson",
    ".json",
}


@router.get("", response_model=PaginatedDocuments)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[uuid.UUID] = None,
    parcel_id: Optional[uuid.UUID] = None,
    doc_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Document)
    count_query = select(func.count(Document.id))

    if project_id:
        query = query.where(Document.project_id == project_id)
        count_query = count_query.where(Document.project_id == project_id)
    if parcel_id:
        query = query.where(Document.parcel_id == parcel_id)
        count_query = count_query.where(Document.parcel_id == parcel_id)
    if doc_type:
        query = query.where(Document.doc_type == doc_type)
        count_query = count_query.where(Document.doc_type == doc_type)

    total = (await db.execute(count_query)).scalar()
    query = (
        query.order_by(Document.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedDocuments(
        items=[DocumentResponse.model_validate(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    parcel_id: Optional[str] = Form(None),
    doc_type: str = Form("other"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate file extension
    ext = os.path.splitext(file.filename or "file")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' is not allowed. Accepted: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Validate MIME type
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MIME type '{file.content_type}' is not allowed. Accepted types: PDF, JPEG, PNG, GIF, DOC, DOCX, XLS, XLSX, CSV, GeoJSON.",
        )

    # Read and validate file size
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size ({len(content) / (1024 * 1024):.1f}MB) exceeds maximum allowed size of {MAX_UPLOAD_SIZE / (1024 * 1024):.0f}MB.",
        )

    # Save file
    upload_dir = os.path.join(settings.UPLOAD_DIR, "documents")
    os.makedirs(upload_dir, exist_ok=True)

    file_id = str(uuid.uuid4())
    file_name = f"{file_id}{ext}"
    file_path = os.path.join(upload_dir, file_name)

    with open(file_path, "wb") as f:
        f.write(content)

    # Store relative path
    relative_path = f"documents/{file_name}"

    doc = Document(
        project_id=uuid.UUID(project_id) if project_id else None,
        parcel_id=uuid.UUID(parcel_id) if parcel_id else None,
        uploaded_by=current_user.id,
        doc_type=doc_type,
        file_name=file.filename or "unknown",
        file_path=relative_path,
        file_size=len(content),
        mime_type=file.content_type,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return DocumentResponse.model_validate(doc)


@router.get("/{doc_id}/versions")
async def get_document_versions(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(Document.parent_document_id == doc_id).order_by(Document.version)
    )
    versions = result.scalars().all()
    return [DocumentResponse.model_validate(v) for v in versions]
