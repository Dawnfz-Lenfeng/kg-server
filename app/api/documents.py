from arq import ArqRedis
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from kgtools.schemas.preprocessing import ExtractConfig, NormalizeConfig

from ..core.response import response_wrapper
from ..dependencies.documents import get_doc, get_doc_svc
from ..dependencies.redis import get_redis
from ..schemas.document import (
    DocCreate,
    DocList,
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
            url=document.url,
            fileName=document.file_name,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{doc_id}/extract")
@response_wrapper
async def extract_doc(
    doc_id: int,
    redis: ArqRedis = Depends(get_redis),
    doc_svc: DocService = Depends(get_doc_svc),
):
    """提取文档 - 异步处理"""
    await doc_svc.update_doc_state(doc_id, DocState.EXTRACTING)

    await redis.enqueue_job("extract_doc", doc_id, ExtractConfig())


@router.put("/{doc_id}/normalize")
@response_wrapper
async def normalize_doc(
    doc_id: int,
    redis: ArqRedis = Depends(get_redis),
    doc_svc: DocService = Depends(get_doc_svc),
):
    """标准化文档 - 异步处理"""
    await doc_svc.update_doc_state(doc_id, DocState.NORMALIZING)

    await redis.enqueue_job("normalize_doc", doc_id, NormalizeConfig())


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
async def get_doc_file(
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


@router.get("")
@response_wrapper
async def get_doc_list(
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(10, ge=1, le=100, description="每页数量"),
    doc_svc: DocService = Depends(get_doc_svc),
) -> DocList:
    """获取文档列表"""
    skip = (page - 1) * pageSize
    items, total = await doc_svc.get_doc_list(skip=skip, limit=pageSize)
    return DocList(
        items=items,
        total=total,
        page=page,
        pageSize=pageSize,
    )


@router.delete("/{doc_id}")
@response_wrapper
async def delete_doc(
    doc_id: int,
    doc_svc: DocService = Depends(get_doc_svc),
):
    """删除文档"""
    if not await doc_svc.delete_doc(doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
