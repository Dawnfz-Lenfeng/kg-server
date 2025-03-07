from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from kgtools.schemas.preprocessing import ExtractConfig, NormalizeConfig

from ..dependencies.documents import get_doc, get_doc_svc
from ..schemas.base import Result, ResultEnum
from ..schemas.document import (
    DocCreate,
    DocResponse,
    DocState,
    DocUpdate,
    FileUploadResult,
)
from ..services import DocService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("")
async def create_doc(
    doc: DocCreate = Depends(get_doc),
    doc_svc: DocService = Depends(get_doc_svc),
):
    """上传文档"""
    try:
        document = await doc_svc.create_doc(doc)
        return FileUploadResult(
            code=200,
            message="上传成功",
            url=f"/api/v1/documents/{document.id}/file",
            fileName=f"{document.title}.{document.file_type}",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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


@router.get("/{doc_id}/file")
async def download_doc_file(
    doc_id: int,
    doc_svc: DocService = Depends(get_doc_svc),
):
    """下载文档文件"""
    doc = await doc_svc.read_doc(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return FileResponse(
        doc.upload_path,
        filename=f"{doc.title}.{doc.file_type}",
        media_type="application/octet-stream",
    )


@router.get("", response_model=list[DocResponse])
async def read_docs(
    skip: int = 0,
    limit: int = 10,
    doc_svc: DocService = Depends(get_doc_svc),
):
    """获取文档列表"""
    return await doc_svc.read_docs(skip, limit)


@router.delete("/{doc_id}", response_model=Result)
async def delete_doc(
    doc_id: int,
    doc_svc: DocService = Depends(get_doc_svc),
):
    """删除文档"""
    if not await doc_svc.delete_doc(doc_id):
        return Result(code=ResultEnum.ERROR, message="Document not found")

    return Result(message="Document deleted")
