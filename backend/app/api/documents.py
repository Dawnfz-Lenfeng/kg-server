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
    if file.filename is None:
        raise HTTPException(status_code=400, detail="File name is required")

    doc_title = title if title is not None else file.filename
    file_type = file.filename.split(".")[-1].lower()

    # 创建文档模型
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
    try:
        if document := await reprocess_document_text(
            db,
            document_id,
            num_workers,
            ocr_engine,
            force_ocr,
            char_threshold,
            sentence_threshold,
        ):
            return document
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Reprocess failed: {str(e)}")


@router.post("/{document_id}/renormalize", response_model=DocumentResponse)
async def renormalize_document_api(
    document_id: int,
    char_threshold: int = 2,
    sentence_threshold: float = 0.9,
    db: Session = Depends(get_db),
):
    """重新清洗文档文本"""
    try:
        if document := await renormalize_document_text(
            db,
            document_id,
            char_threshold,
            sentence_threshold,
        ):
            return document
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Renormalize failed: {str(e)}")


@router.get("/{document_id}", response_model=DocumentResponse)
async def read_document(
    document_id: int, include_origin: bool = False, db: Session = Depends(get_db)
):
    """获取单个文档"""
    if document := await get_document(db, document_id):
        response = document.__dict__.copy()
        if not include_origin:
            response.pop("origin_text", None)
        return response
    raise HTTPException(status_code=404, detail="Document not found")


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
    if updated := await update_document(db, document_id, document):
        return updated
    raise HTTPException(status_code=404, detail="Document not found")


@router.delete("/{document_id}")
async def delete_document_api(document_id: int, db: Session = Depends(get_db)):
    """删除文档"""
    if await delete_document(db, document_id):
        return {"message": "Document deleted"}
    raise HTTPException(status_code=404, detail="Document not found")
