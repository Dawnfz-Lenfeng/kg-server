from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.document import DocUploadResult

from ..database import get_db
from ..schemas.document import DocCreate, DocDetailResponse, DocResponse, DocUpdate
from ..schemas.preprocessing import ExtractConfig, NormalizeConfig
from ..services.document import (
    create_doc_service,
    delete_doc_service,
    extract_doc_text_service,
    get_doc,
    get_docs,
    normalize_doc_text_service,
    read_doc_service,
    read_docs_service,
    update_doc_service,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocUploadResult)
async def create_doc(
    doc: DocCreate = Depends(get_doc),
    db: Session = Depends(get_db),
) -> DocUploadResult:
    """上传文档"""
    try:
        document = create_doc_service(doc, db)
        return DocUploadResult(
            success=True,
            document=DocDetailResponse.model_validate(document),
            error=None,
        )
    except Exception as e:
        return DocUploadResult(success=False, document=None, error=str(e))


@router.post("/batch", response_model=list[DocUploadResult])
async def create_docs(
    docs: list[DocCreate] = Depends(get_docs),
    db: Session = Depends(get_db),
) -> list[DocUploadResult]:
    """批量上传文档"""
    results = []
    for doc in docs:
        try:
            document = create_doc_service(doc, db)
            results.append(
                DocUploadResult(
                    success=True,
                    document=DocDetailResponse.model_validate(document),
                    error=None,
                )
            )
        except Exception as e:
            results.append(DocUploadResult(success=False, document=None, error=str(e)))
    return results


@router.put("/{doc_id}/extract", response_model=DocDetailResponse)
def extract_doc_text(
    doc_id: int,
    extract_config: ExtractConfig = Body(default=ExtractConfig()),
    db: Session = Depends(get_db),
):
    """提取文档文本"""
    return extract_doc_text_service(doc_id, extract_config, db)


@router.put("/{doc_id}/normalize", response_model=DocDetailResponse)
def normalize_doc_text(
    doc_id: int,
    normalize_config: NormalizeConfig = Body(default=NormalizeConfig()),
    db: Session = Depends(get_db),
):
    """清洗文档文本"""
    return normalize_doc_text_service(doc_id, normalize_config, db)


@router.put("/{doc_id}", response_model=DocResponse)
def update_doc(
    doc_id: int,
    doc: DocUpdate,
    db: Session = Depends(get_db),
):
    """更新文档"""
    updated = update_doc_service(doc_id, doc, db)
    if updated is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return updated


@router.get("/{doc_id}", response_model=DocDetailResponse)
def read_doc(
    doc_id: int,
    db: Session = Depends(get_db),
):
    """获取文档"""
    doc = read_doc_service(doc_id, db)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("", response_model=list[DocResponse])
def read_docs(
    skip: int = 0,
    limit: int = 10,
    subject_id: int | None = None,
    db: Session = Depends(get_db),
):
    """获取文档列表"""
    return read_docs_service(skip, limit, subject_id, db)


@router.delete("/{doc_id}")
def delete_doc(
    doc_id: int,
    db: Session = Depends(get_db),
):
    """删除文档"""
    if not delete_doc_service(doc_id, db):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted"}
