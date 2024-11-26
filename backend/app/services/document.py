import asyncio
import os
import uuid
from pathlib import Path

from fastapi import File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..config import settings
from ..database import transaction
from ..models.document import Document
from ..models.keyword import Keyword
from ..preprocessing import extract_text, normalize_text
from ..schemas.document import DocCreate, DocUpdate, DocUploadResult, FileType
from ..schemas.preprocessing import ExtractConfig, NormalizeConfig


def get_unique_filename(original_name: str) -> str:
    """生成唯一文件名"""
    stem = Path(original_name).stem
    suffix = Path(original_name).suffix
    return f"{stem}_{uuid.uuid4().hex[:8]}{suffix}"


async def get_doc(
    file: UploadFile = File(...),
    subject_id: int = Form(..., examples=[1, 2, 3, 4]),
    title: str | None = Form(None),
    file_type: FileType | None = Form(None),
    keyword_ids: list[int] | None = Form(None, examples=[[1, 2]]),
):
    """依赖函数，解析文档上传的表单数据"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    unique_filename = get_unique_filename(file.filename)
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return DocCreate(
        title=title or Path(file.filename).stem,
        file_path=file_path,
        file_type=file_type or Path(file.filename).suffix[1:],
        subject_id=subject_id,
        keyword_ids=keyword_ids,
    )


async def get_docs(
    files: list[UploadFile] = File(...),
    subject_id: int = Form(..., examples=[1, 2, 3, 4]),
    titles: list[str] | None = Form(None),
    file_type: FileType | None = Form(None),
) -> list[DocCreate]:
    if titles is not None and len(files) != len(titles):
        raise HTTPException(status_code=400, detail="文件数量与标题数量不匹配")

    tasks = [
        get_doc(
            file=file,
            title=title,
            file_type=file_type,
            subject_id=subject_id,
            keyword_ids=None,
        )
        for file, title in zip(files, titles or [None] * len(files))
    ]

    result = await asyncio.gather(*tasks)
    return result


async def create_doc_service(
    doc: DocCreate,
    db: Session,
) -> DocUploadResult:
    """创建文档"""
    try:
        with transaction(db):
            db_doc = Document(
                **doc.model_dump(exclude={"keyword_ids"}, exclude_unset=True)
            )

            if doc.keyword_ids:
                stmt = select(Keyword).where(Keyword.id.in_(doc.keyword_ids))
                keywords = set(db.execute(stmt).scalars().all())
                db_doc.keywords = keywords

            db.add(db_doc)

        db.refresh(db_doc)
        return DocUploadResult(success=True, document=db_doc, error=None)

    except Exception as e:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
        return DocUploadResult(success=False, document=None, error=str(e))


async def create_docs_service(
    docs: list[DocCreate],
    db: Session,
) -> list[DocUploadResult]:
    """批量上传文档"""
    tasks = [create_doc_service(doc, db) for doc in docs]

    results = await asyncio.gather(*tasks)
    return results


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
        with transaction(db):
            db.add(doc)

        db.refresh(doc)
        return doc
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Text extracting failed: {str(e)}"
        ) from e


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

    with transaction(db):
        db.add(doc)

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
) -> list[Document]:
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

    with transaction(db):
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

        db.add(doc)

    db.refresh(doc)
    return doc


async def delete_doc_service(
    doc_id: int,
    db: Session,
) -> bool:
    """删除文档"""
    stmt = select(Document).where(Document.id == doc_id)
    db_doc = db.execute(stmt).scalar_one_or_none()

    if db_doc is not None:
        with transaction(db):
            db.delete(db_doc)
        return True

    return False
