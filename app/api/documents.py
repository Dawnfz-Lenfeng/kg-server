from arq import ArqRedis
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from kgtools.schemas.preprocessing import ExtractConfig, NormalizeConfig

from ..core.response import to_response
from ..dependencies.documents import get_doc, get_doc_svc
from ..dependencies.redis import get_redis
from ..schemas.base import Page
from ..schemas.document import DocCreate, DocState, DocUpdate, FileUploadResult
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
@to_response
async def extract_doc(
    doc_id: int,
    redis: ArqRedis = Depends(get_redis),
):
    """提取文档 - 异步处理"""
    await redis.enqueue_job("extract_doc", doc_id, ExtractConfig())


@router.put("/{doc_id}/normalize")
@to_response
async def normalize_doc(
    doc_id: int,
    redis: ArqRedis = Depends(get_redis),
):
    """标准化文档 - 异步处理"""
    await redis.enqueue_job("normalize_doc", doc_id, NormalizeConfig())


@router.put("/{doc_id}")
async def update_doc(
    doc_id: int,
    doc: DocUpdate,
    doc_svc: DocService = Depends(get_doc_svc),
):
    """更新文档"""
    updated = await doc_svc.update_doc(doc_id, doc)
    if updated is None:
        raise HTTPException(status_code=404, detail="Document not found")


@router.get("/{doc_id}/download")
async def download_doc(
    doc_id: int,
    state: DocState = Query(DocState.UPLOADED, description="下载文件状态"),
    doc_svc: DocService = Depends(get_doc_svc),
):
    """下载文档文件"""
    path, filename = await doc_svc.download_doc(doc_id, state)
    return FileResponse(
        path,
        filename=filename,
        media_type="application/octet-stream",
    )


@router.get("")
@to_response
async def get_doc_list(
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(10, ge=1, le=100, description="每页数量"),
    doc_svc: DocService = Depends(get_doc_svc),
):
    """获取文档列表"""
    skip = (page - 1) * pageSize
    items, total = await doc_svc.get_doc_list(skip=skip, limit=pageSize)
    return Page(
        items=items,
        total=total,
        page=page,
        pageSize=pageSize,
    )


@router.delete("/{doc_id}")
@to_response
async def delete_doc(
    doc_id: int,
    doc_svc: DocService = Depends(get_doc_svc),
):
    """删除文档"""
    if not await doc_svc.delete_doc(doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
