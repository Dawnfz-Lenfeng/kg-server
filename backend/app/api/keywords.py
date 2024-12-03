from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session


from ..dependencies.keywords import get_kw_svc
from ..schemas.keyword import (
    KeywordCreate,
    KeywordDetailResponse,
    KeywordResponse,
    KeywordUpdate,
)
from ..services.keyword import (
    create_keyword_service,
    delete_keyword_service,
    read_keyword_service,
    read_keywords_service,
    update_keyword_service,
)

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.post("", response_model=KeywordDetailResponse)
async def create_keyword(
    keyword: KeywordCreate,
    db: Session = Depends(get_kw_svc),
):
    """创建关键词"""
    return await create_keyword_service(keyword, db)


@router.get("/{keyword_id}", response_model=KeywordDetailResponse)
async def read_keyword(
    keyword_id: int,
    db: Session = Depends(get_kw_svc),
):
    """获取关键词"""
    keyword = read_keyword_service(keyword_id, db)
    if keyword is None:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return keyword


@router.get("", response_model=list[KeywordResponse])
async def read_keywords(
    skip: int = 0,
    limit: int = 10,
    search: str | None = Query(None, description="搜索关键词名称"),
    db: Session = Depends(get_kw_svc),
):
    """获取关键词列表"""
    return read_keywords_service(skip, limit, search, db)


@router.put("/{keyword_id}", response_model=KeywordDetailResponse)
async def update_keyword(
    keyword_id: int,
    keyword: KeywordUpdate,
    db: Session = Depends(get_kw_svc),
):
    """更新关键词"""
    updated = await update_keyword_service(keyword_id, keyword, db)
    if updated is None:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return updated


@router.delete("/{keyword_id}")
async def delete_keyword(
    keyword_id: int,
    db: Session = Depends(get_kw_svc),
):
    """删除关键词"""
    if not await delete_keyword_service(keyword_id, db):
        raise HTTPException(status_code=404, detail="Keyword not found")
    return {"message": "Keyword deleted"}
