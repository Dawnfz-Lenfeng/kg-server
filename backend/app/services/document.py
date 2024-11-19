from __future__ import annotations

from typing import Sequence

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.document import Document
from ..preprocessing import extract_text, normalize_text
from ..schemas.document import DocumentCreate, DocumentUpdate


async def create_document(
    db: Session,
    document: DocumentCreate,
    file: UploadFile,
    num_workers: int = 4,
    ocr_engine: str = "cnocr",
    force_ocr: bool = False,
    char_threshold: int = 2,
    sentence_threshold: float = 0.9,
    upload_dir: str = "uploads",
) -> Document:
    """创建新文档"""
    import os
    from typing import cast

    # 保存文件
    file_path = os.path.join(upload_dir, cast(str, file.filename))
    os.makedirs(upload_dir, exist_ok=True)

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")

    # 创建文档记录
    db_document = Document(
        title=document.title,
        file_path=file_path,
        file_type=document.file_type,
        subject_id=document.subject_id,
    )

    # 处理文档文本
    try:
        db_document.origin_text = extract_text(
            file_path,
            ocr_engine=ocr_engine,
            num_workers=num_workers,
            force_ocr=force_ocr,
        )
        db_document.processed_text = normalize_text(
            db_document.origin_text,
            char_threshold=char_threshold,
            sentence_threshold=sentence_threshold,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Text extraction failed: {str(e)}")

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return db_document


async def get_document(db: Session, document_id: int) -> Document | None:
    """获取单个文档"""
    stmt = select(Document).where(Document.id == document_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()


async def get_documents(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    subject_id: int | None = None,
) -> Sequence[Document]:
    """获取文档列表"""
    stmt = select(Document)
    if subject_id is not None:
        stmt = stmt.where(Document.subject_id == subject_id)
    stmt = stmt.offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


async def update_document(
    db: Session, document_id: int, document_update: DocumentUpdate
) -> Document | None:
    """更新文档"""
    db_document = await get_document(db, document_id)
    if db_document is not None:
        update_data = document_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_document, key, value)
        db.commit()
        db.refresh(db_document)
    return db_document


async def delete_document(db: Session, document_id: int) -> bool:
    """删除文档"""
    stmt = select(Document).where(Document.id == document_id)
    db_document = db.execute(stmt).scalar_one_or_none()
    if db_document is not None:
        db.delete(db_document)
        db.commit()
        return True
    return False


async def reprocess_document_text(
    db: Session,
    document_id: int,
    num_workers: int = 4,
    ocr_engine: str = "cnocr",
    force_ocr: bool = False,
    char_threshold: int = 2,
    sentence_threshold: float = 0.9,
) -> Document | None:
    """重新处理文档文本"""
    document = await get_document(db, document_id)
    if document is None:
        return None

    document.origin_text = extract_text(
        document.file_path,
        ocr_engine=ocr_engine,
        num_workers=num_workers,
        force_ocr=force_ocr,
    )
    document.processed_text = normalize_text(
        document.origin_text,
        char_threshold=char_threshold,
        sentence_threshold=sentence_threshold,
    )
    db.commit()
    db.refresh(document)
    return document


async def renormalize_document_text(
    db: Session,
    document_id: int,
    char_threshold: int = 2,
    sentence_threshold: float = 0.9,
) -> Document | None:
    """重新清洗文档文本"""
    document = await get_document(db, document_id)
    if document is None:
        return None

    document.processed_text = normalize_text(
        document.origin_text,
        char_threshold=char_threshold,
        sentence_threshold=sentence_threshold,
    )
    db.commit()
    db.refresh(document)
    return document
