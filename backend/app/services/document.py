from typing import Sequence

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..models.document import Document
from ..preprocessing import extract_text, normalize_text
from ..schemas.document import DocumentCreate, DocumentUpdate
from ..schemas.preprocessing import ExtractConfig, NormalizeConfig


async def create_doc_service(
    doc: DocumentCreate,
    file: UploadFile,
    db: Session,
    upload_dir: str = settings.UPLOAD_DIR,
) -> Document:
    """create new document"""
    import os
    from typing import cast

    file_path = os.path.join(upload_dir, cast(str, file.filename))
    os.makedirs(upload_dir, exist_ok=True)

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"File upload failed: {str(e)}"
        ) from e

    db_doc = Document(
        title=doc.title,
        file_path=file_path,
        file_type=doc.file_type,
        subject_id=doc.subject_id,
    )

    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc


async def extract_doc_text_service(
    doc_id: int,
    extract_config: ExtractConfig,
    db: Session,
) -> Document | None:
    """Extract document text"""
    doc = await read_doc_service(doc_id, db)
    if doc is None:
        return None

    try:
        doc.origin_text = extract_text(
            doc.file_path,
            file_type=doc.file_type,
            **extract_config.model_dump(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Text extracting failed: {str(e)}"
        ) from e

    db.commit()
    db.refresh(doc)
    return doc


async def normalize_doc_text_service(
    doc_id: int,
    normalize_config: NormalizeConfig,
    db: Session,
) -> Document | None:
    """Normalize document text"""
    doc = await read_doc_service(doc_id, db)
    if doc is None:
        return None

    doc.processed_text = normalize_text(
        doc.origin_text,
        **normalize_config.model_dump(),
    )
    db.commit()
    db.refresh(doc)
    return doc


async def read_doc_service(
    doc_id: int,
    db: Session,
) -> Document | None:
    """Find single document"""
    stmt = select(Document).where(Document.id == doc_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()


async def read_docs_service(
    skip: int,
    limit: int,
    subject_id: int | None,
    db: Session,
) -> Sequence[Document]:
    """Find documents"""
    stmt = select(Document)
    if subject_id is not None:
        stmt = stmt.where(Document.subject_id == subject_id)
    stmt = stmt.offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


async def update_doc_service(
    doc_id: int,
    doc_update: DocumentUpdate,
    db: Session,
) -> Document | None:
    """Update document"""
    db_doc = await read_doc_service(doc_id, db)
    if db_doc is not None:
        update_data = doc_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_doc, key, value)
        db.commit()
        db.refresh(db_doc)
    return db_doc


async def delete_doc_service(
    doc_id: int,
    db: Session,
) -> bool:
    """Delete document"""
    stmt = select(Document).where(Document.id == doc_id)
    db_doc = db.execute(stmt).scalar_one_or_none()
    if db_doc is not None:
        db.delete(db_doc)
        db.commit()
        return True
    return False
