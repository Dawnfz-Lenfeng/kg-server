import os
from pathlib import Path
from typing import Sequence

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..config import settings
from ..models.document import Document
from ..models.keyword import Keyword
from ..preprocessing import extract_text, normalize_text
from ..schemas.document import DocCreate, DocUpdate
from ..schemas.preprocessing import ExtractConfig, NormalizeConfig


async def create_doc_service(
    file: UploadFile,
    doc: DocCreate,
    db: Session,
    upload_dir: str = settings.UPLOAD_DIR,
) -> Document:
    """上传并创建文档"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    path = Path(file.filename)

    file_path = os.path.join(upload_dir, file.filename)
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
        title=doc.title or path.stem,
        file_path=file_path,
        file_type=doc.file_type or path.suffix[1:],
        subject_id=doc.subject_id,
    )

    if doc.keyword_ids:
        stmt = select(Keyword).where(Keyword.id.in_(doc.keyword_ids))
        keywords = set(db.execute(stmt).scalars().all())
        db_doc.keywords = keywords

    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc


async def extract_doc_text_service(
    doc_id: int,
    extract_config: ExtractConfig,
    db: Session,
) -> Document | None:
    """提取文档文本"""
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
    """标准化文档文本"""
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
    """获取单个文档"""
    stmt = (
        select(Document)
        .where(Document.id == doc_id)
        .options(selectinload(Document.keywords))
    )
    result = db.execute(stmt)
    return result.scalar_one_or_none()


async def read_docs_service(
    skip: int,
    limit: int,
    subject_id: int | None,
    db: Session,
) -> Sequence[Document]:
    """获取文档列表"""
    stmt = select(Document).options(selectinload(Document.keywords))  # 预加载关键词
    if subject_id is not None:
        stmt = stmt.where(Document.subject_id == subject_id)
    stmt = stmt.offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


async def update_doc_service(
    doc_id: int,
    doc_update: DocUpdate,
    db: Session,
) -> Document | None:
    """更新文档信息，包括基本信息和关键词"""
    doc = await read_doc_service(doc_id, db)
    if doc is None:
        return None

    update_data = doc_update.model_dump(exclude={"keywords"}, exclude_unset=True)
    for key, value in update_data.items():
        setattr(doc, key, value)

    if doc_update.keywords is not None:
        keywords_update = doc_update.keywords

        if keywords_update.add:
            stmt = select(Keyword).where(Keyword.id.in_(keywords_update.add))
            keywords_to_add = set(db.execute(stmt).scalars().all())
            doc.keywords |= keywords_to_add

        if keywords_update.remove:
            stmt = select(Keyword).where(Keyword.id.in_(keywords_update.remove))
            keywords_to_remove = set(db.execute(stmt).scalars().all())
            doc.keywords -= keywords_to_remove

    db.commit()
    db.refresh(doc)
    return doc


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
