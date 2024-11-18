from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from ..models.document import Document
from ..preprocessing.extract_text import extract_text
from ..preprocessing.normolize_text import normalize_text
from ..schemas.document import DocumentCreate, DocumentUpdate


async def create_document(
    db: Session, document: DocumentCreate, file: UploadFile, upload_dir: str = "uploads"
) -> Document:
    """创建新文档"""
    import os

    from fastapi import HTTPException

    # 保存文件
    file_path = os.path.join(upload_dir, file.filename)
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
        raw_text = extract_text(file_path)
        db_document.processed_text = normalize_text(raw_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Text extraction failed: {str(e)}")

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return db_document


async def get_document(db: Session, document_id: int) -> Optional[Document]:
    """获取单个文档"""
    return db.query(Document).filter(Document.id == document_id).first()


async def get_documents(
    db: Session, skip: int = 0, limit: int = 10, subject_id: Optional[int] = None
) -> List[Document]:
    """获取文档列表"""
    query = db.query(Document)
    if subject_id:
        query = query.filter(Document.subject_id == subject_id)
    return query.offset(skip).limit(limit).all()


async def update_document(
    db: Session, document_id: int, document_update: DocumentUpdate
) -> Optional[Document]:
    """更新文档"""
    db_document = await get_document(db, document_id)
    if db_document:
        update_data = document_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_document, key, value)
        db.commit()
        db.refresh(db_document)
    return db_document


async def delete_document(db: Session, document_id: int) -> bool:
    """删除文档"""
    db_document = await get_document(db, document_id)
    if db_document:
        db.delete(db_document)
        db.commit()
        return True
    return False
