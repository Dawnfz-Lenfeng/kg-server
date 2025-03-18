from fastapi import APIRouter, Depends, HTTPException, Query

from ..core.response import to_response
from ..dependencies.keyword import get_keywords, get_kw_svc
from ..schemas.base import Page
from ..schemas.keyword import KeywordCreate
from ..schemas.subject import Subject
from ..services import KeywordService

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.post("")
@to_response
async def create_keyword(
    keyword: KeywordCreate,
    kw_svc: KeywordService = Depends(get_kw_svc),
):
    """创建关键词"""
    await kw_svc.create_keyword(keyword)


@router.post("/upload")
@to_response
async def create_keywords(
    keywords: list[KeywordCreate] = Depends(get_keywords),
    kw_svc: KeywordService = Depends(get_kw_svc),
):
    """批量上传关键词"""
    for keyword in keywords:
        try:
            await kw_svc.create_keyword(keyword)
        except ValueError:
            continue


@router.get("")
@to_response
async def get_keyword_list(
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(10, ge=1, le=100, description="每页数量"),
    subject: list[Subject] | None = Query(None, description="学科列表"),
    kw_svc: KeywordService = Depends(get_kw_svc),
):
    """获取关键词列表"""
    skip = (page - 1) * pageSize
    items, total = await kw_svc.get_keyword_list(
        skip=skip, limit=pageSize, subject=subject
    )
    return Page(
        items=items,
        total=total,
        page=page,
        pageSize=pageSize,
    )


@router.delete("/{keyword_id}")
@to_response
async def delete_keyword(
    keyword_id: int,
    kw_svc: KeywordService = Depends(get_kw_svc),
):
    """删除关键词"""
    if not await kw_svc.delete_keyword(keyword_id):
        raise HTTPException(status_code=404, detail="Keyword not found")
