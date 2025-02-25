from fastapi import APIRouter, Body, Depends, HTTPException, Query
from kgtools.schemas.preprocessing import ExtractConfig, NormalizeConfig

from ..dependencies.documents import get_doc, get_doc_svc, get_docs
from ..schemas.document import (
    DocCreate,
    DocResponse,
    DocState,
    DocUpdate,
    DocUploadResult,
)
from ..services import DocService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocUploadResult)
async def create_doc(
    doc: DocCreate = Depends(get_doc),
    doc_svc: DocService = Depends(get_doc_svc),
) -> DocUploadResult:
    """上传文档"""
    try:
        document = await doc_svc.create_doc(doc)
        return DocUploadResult(
            success=True,
            document=DocResponse.model_validate(document),
            error=None,
        )
    except Exception as e:
        return DocUploadResult(success=False, document=None, error=str(e))


@router.post("/batch", response_model=list[DocUploadResult])
async def create_docs(
    docs: list[DocCreate] = Depends(get_docs),
    doc_svc: DocService = Depends(get_doc_svc),
) -> list[DocUploadResult]:
    """批量上传文档"""
    results = []
    for doc in docs:
        try:
            document = await doc_svc.create_doc(doc)
            results.append(
                DocUploadResult(
                    success=True,
                    document=DocResponse.model_validate(document),
                    error=None,
                )
            )
        except Exception as e:
            results.append(DocUploadResult(success=False, document=None, error=str(e)))
    return results


@router.put("/{doc_id}/extract", response_model=DocResponse)
async def extract_doc_text(
    doc_id: int,
    extract_config: ExtractConfig = Body(default=ExtractConfig()),
    doc_svc: DocService = Depends(get_doc_svc),
):
    """提取文档文本"""
    doc = await doc_svc.extract_doc_text(doc_id, extract_config)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/{doc_id}/normalize", response_model=DocResponse)
async def normalize_doc_text(
    doc_id: int,
    normalize_config: NormalizeConfig = Body(default=NormalizeConfig()),
    doc_svc: DocService = Depends(get_doc_svc),
):
    """清洗文档文本"""
    doc = await doc_svc.normalize_doc_text(doc_id, normalize_config)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/{doc_id}", response_model=DocResponse)
async def update_doc(
    doc_id: int,
    doc: DocUpdate,
    doc_svc: DocService = Depends(get_doc_svc),
):
    """更新文档"""
    updated = await doc_svc.update_doc(doc_id, doc)
    if updated is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return updated


@router.get("/{doc_id}", response_model=DocResponse)
async def read_doc(
    doc_id: int,
    doc_svc: DocService = Depends(get_doc_svc),
):
    """获取文档"""
    doc = await doc_svc.read_doc(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/{doc_id}/text")
async def read_doc_text(
    doc_id: int,
    normalized: bool = Query(True, description="是否获取标准化文本"),
    doc_svc: DocService = Depends(get_doc_svc),
) -> str:
    """获取文档文本内容"""
    state = DocState.NORMALIZED if normalized else DocState.EXTRACTED
    text = await doc_svc.read_doc_text(doc_id, state)
    if text is None:
        raise HTTPException(status_code=404, detail="Document text not found")
    return text


@router.get("", response_model=list[DocResponse])
async def read_docs(
    skip: int = 0,
    limit: int = 10,
    subject_id: int | None = None,
    doc_svc: DocService = Depends(get_doc_svc),
):
    """获取文档列表"""
    return await doc_svc.read_docs(skip, limit, subject_id)


@router.delete("/{doc_id}")
async def delete_doc(
    doc_id: int,
    doc_svc: DocService = Depends(get_doc_svc),
):
    """删除文档"""
    if not await doc_svc.delete_doc(doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted"}
