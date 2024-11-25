from pathlib import Path

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.document import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
)
from ..schemas.preprocessing import ExtractConfig, NormalizeConfig
from ..services.document import (
    create_doc_service,
    delete_doc_service,
    extract_doc_text_service,
    normalize_doc_text_service,
    read_doc_service,
    read_docs_service,
    update_doc_service,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentResponse)
async def create_doc(
    file: UploadFile = File(...),
    title: str | None = Form(
        None, description="Optional custom title, if not provided, use file name"
    ),
    subject_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """上传文档"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    path = Path(file.filename)
    doc = DocumentCreate(
        title=title or path.stem,
        file_type=path.suffix[1:],
        subject_id=subject_id,
    )
    return await create_doc_service(doc, file, db)


@router.post("/{doc_id}/extract", response_model=DocumentResponse)
async def extract_doc_text(
    doc_id: int,
    extract_config: ExtractConfig = Body(default=ExtractConfig()),
    db: Session = Depends(get_db),
):
    """提取文档文本"""
    return await extract_doc_text_service(doc_id, extract_config, db)


@router.post("/{doc_id}/normalize", response_model=DocumentResponse)
async def normalize_doc_text(
    doc_id: int,
    normalize_config: NormalizeConfig = Body(default=NormalizeConfig()),
    db: Session = Depends(get_db),
):
    """清洗文档文本"""
    return await normalize_doc_text_service(doc_id, normalize_config, db)


@router.get("/{doc_id}", response_model=DocumentResponse)
async def read_doc(
    doc_id: int,
    db: Session = Depends(get_db),
):
    """获取文档"""
    doc = await read_doc_service(doc_id, db)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/", response_model=list[DocumentListResponse])
async def read_docs(
    skip: int = 0,
    limit: int = 10,
    subject_id: int | None = None,
    db: Session = Depends(get_db),
):
    """获取文档列表"""
    return await read_docs_service(skip, limit, subject_id, db)


@router.put("/{doc_id}", response_model=DocumentResponse)
async def update_doc(
    doc_id: int,
    doc: DocumentUpdate,
    db: Session = Depends(get_db),
):
    """更新文档"""
    updated = await update_doc_service(doc_id, doc, db)
    if updated is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return updated


@router.delete("/{doc_id}")
async def delete_doc(
    doc_id: int,
    db: Session = Depends(get_db),
):
    """删除文档"""
    if not await delete_doc_service(doc_id, db):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted"}
