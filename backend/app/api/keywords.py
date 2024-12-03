from fastapi import APIRouter, Depends, HTTPException, Query

from ..dependencies.keywords import get_kw_svc
from ..schemas.keyword import (
    KeywordCreate,
    KeywordDetailResponse,
    KeywordResponse,
    KeywordUpdate,
)
from ..services.keyword import KeywordService

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.post("", response_model=KeywordDetailResponse)
async def create_keyword(
    keyword: KeywordCreate,
    kw_svc: KeywordService = Depends(get_kw_svc),
):
    """创建关键词"""
    return await kw_svc.create_keyword(keyword)


@router.get("/{keyword_id}", response_model=KeywordDetailResponse)
async def read_keyword(
    keyword_id: int,
    kw_svc: KeywordService = Depends(get_kw_svc),
):
    """获取关键词"""
    keyword = await kw_svc.read_keyword(keyword_id)
    if keyword is None:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return keyword


@router.get("", response_model=list[KeywordResponse])
async def read_keywords(
    skip: int = 0,
    limit: int = 10,
    search: str | None = Query(None, description="搜索关键词名称"),
    kw_svc: KeywordService = Depends(get_kw_svc),
):
    """获取关键词列表"""
    return await kw_svc.read_keywords(skip, limit, search)


@router.put("/{keyword_id}", response_model=KeywordDetailResponse)
async def update_keyword(
    keyword_id: int,
    keyword: KeywordUpdate,
    kw_svc: KeywordService = Depends(get_kw_svc),
):
    """更新关键词"""
    updated = await kw_svc.update_keyword(keyword_id, keyword)
    if updated is None:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return updated


@router.delete("/{keyword_id}")
async def delete_keyword(
    keyword_id: int,
    kw_svc: KeywordService = Depends(get_kw_svc),
):
    """删除关键词"""
    if not await kw_svc.delete_keyword(keyword_id):
        raise HTTPException(status_code=404, detail="Keyword not found")
    return {"message": "Keyword deleted"}
