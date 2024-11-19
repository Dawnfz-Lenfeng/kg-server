from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.document import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
)
from ..services.document import (
    create_document,
    delete_document,
    get_document,
    get_documents,
    renormalize_document_text,
    reprocess_document_text,
    update_document,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    subject_id: int | None = None,
    num_workers: int = 4,
    ocr_engine: str = "cnocr",
    force_ocr: bool = False,
    char_threshold: int = 2,
    sentence_threshold: float = 0.9,
    db: Session = Depends(get_db),
):
    """上传新文档"""
    import os

    if file.filename is None:
        raise HTTPException(status_code=400, detail="File name is required")

    file_name, file_type = os.path.splitext(file.filename)
    doc_title = title or file_name

    document = DocumentCreate(
        title=doc_title, file_type=file_type, subject_id=subject_id
    )

    return await create_document(
        db,
        document,
        file,
        num_workers=num_workers,
        ocr_engine=ocr_engine,
        force_ocr=force_ocr,
        char_threshold=char_threshold,
        sentence_threshold=sentence_threshold,
    )


@router.post("/{document_id}/reprocess", response_model=DocumentResponse)
async def reprocess_document_api(
    document_id: int,
    num_workers: int = 4,
    ocr_engine: str = "cnocr",
    force_ocr: bool = False,
    char_threshold: int = 2,
    sentence_threshold: float = 0.9,
    db: Session = Depends(get_db),
):
    """重新提取文档文本"""
    document = await reprocess_document_text(
        db,
        document_id,
        num_workers,
        ocr_engine,
        force_ocr,
        char_threshold,
        sentence_threshold,
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/{document_id}/renormalize", response_model=DocumentResponse)
async def renormalize_document_api(
    document_id: int,
    char_threshold: int = 2,
    sentence_threshold: float = 0.9,
    db: Session = Depends(get_db),
):
    """重新清洗文档文本"""
    document = await renormalize_document_text(
        db,
        document_id,
        char_threshold,
        sentence_threshold,
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{document_id}", response_model=DocumentResponse)
async def read_document(
    document_id: int, include_origin: bool = False, db: Session = Depends(get_db)
):
    """获取单个文档"""
    document = await get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    response = document.__dict__.copy()
    if not include_origin:
        response.pop("origin_text", None)
    return response


@router.get("/", response_model=list[DocumentListResponse])
async def read_documents(
    skip: int = 0,
    limit: int = 10,
    subject_id: int | None = None,
    db: Session = Depends(get_db),
):
    """获取文档列表"""
    return await get_documents(db, skip, limit, subject_id)


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document_api(
    document_id: int, document: DocumentUpdate, db: Session = Depends(get_db)
):
    """更新文档"""
    updated = await update_document(db, document_id, document)
    if updated is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return updated


@router.delete("/{document_id}")
async def delete_document_api(document_id: int, db: Session = Depends(get_db)):
    """删除文档"""
    if not await delete_document(db, document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted"}
