from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from ..services.document import (
    create_document,
    delete_document,
    get_document,
    get_documents,
    update_document,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    subject_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """上传新文档"""
    # 使用文件名作为标题（如果未提供）
    if not title:
        title = file.filename

    # 获取文件类型
    file_type = file.filename.split(".")[-1].lower()

    # 创建文档模型
    document = DocumentCreate(title=title, file_type=file_type, subject_id=subject_id)

    return await create_document(db, document, file)


@router.get("/{document_id}", response_model=DocumentResponse)
async def read_document(document_id: int, db: Session = Depends(get_db)):
    """获取单个文档"""
    if document := await get_document(db, document_id):
        return document
    raise HTTPException(status_code=404, detail="Document not found")


@router.get("/", response_model=List[DocumentResponse])
async def read_documents(
    skip: int = 0,
    limit: int = 10,
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """获取文档列表"""
    return await get_documents(db, skip, limit, subject_id)


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document_api(
    document_id: int, document: DocumentUpdate, db: Session = Depends(get_db)
):
    """更新文档"""
    if updated := await update_document(db, document_id, document):
        return updated
    raise HTTPException(status_code=404, detail="Document not found")


@router.delete("/{document_id}")
async def delete_document_api(document_id: int, db: Session = Depends(get_db)):
    """删除文档"""
    if await delete_document(db, document_id):
        return {"message": "Document deleted"}
    raise HTTPException(status_code=404, detail="Document not found")
