from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.keyword import DocumentKeywordResponse, KeywordResponse
from ..services.keyword import (
    create_document_keyword,
    create_keyword,
    delete_document_keyword,
    delete_keyword,
    get_document_keywords,
    get_keyword,
    get_keywords,
)

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.post("/", response_model=KeywordResponse)
async def create_keyword_api(
    keyword_name: str,
    db: Session = Depends(get_db),
):
    """创建关键词"""
    return await create_keyword(db, keyword_name)


@router.get("/search", response_model=KeywordResponse)
async def search_keyword(
    keyword_id: Optional[int] = None,
    keyword_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """通过ID或名称搜索关键词"""
    if not (keyword_id or keyword_name):
        raise HTTPException(
            status_code=400, detail="Either keyword_id or keyword_name must be provided"
        )

    if keyword := await get_keyword(db, keyword_id, keyword_name):
        return keyword
    raise HTTPException(status_code=404, detail="Keyword not found")


@router.get("/", response_model=List[KeywordResponse])
async def read_keywords(
    skip: int = 0,
    limit: int = 10,
    search_name: Optional[str] = Query(None, description="搜索关键词名称"),
    db: Session = Depends(get_db),
):
    """获取关键词列表，支持搜索"""
    return await get_keywords(db, skip, limit, search_name)


@router.get("/{keyword_id}", response_model=KeywordResponse)
async def read_keyword(keyword_id: int, db: Session = Depends(get_db)):
    """通过ID获取单个关键词"""
    if keyword := await get_keyword(db, keyword_id=keyword_id):
        return keyword
    raise HTTPException(status_code=404, detail="Keyword not found")


@router.delete("/{keyword_id}")
async def delete_keyword_api(keyword_id: int, db: Session = Depends(get_db)):
    """删除关键词"""
    if await delete_keyword(db, keyword_id):
        return {"message": "Keyword deleted"}
    raise HTTPException(status_code=404, detail="Keyword not found")


# 文档关键词关联接口
@router.post("/document/{document_id}", response_model=DocumentKeywordResponse)
async def create_document_keyword_api(
    document_id: int,
    keyword_id: int,
    db: Session = Depends(get_db),
):
    """为文档添加关键词"""
    if doc_keyword := await create_document_keyword(db, document_id, keyword_id):
        return doc_keyword
    raise HTTPException(status_code=404, detail="Document or keyword not found")


@router.get("/document/{document_id}", response_model=List[DocumentKeywordResponse])
async def read_document_keywords_api(
    document_id: int,
    db: Session = Depends(get_db),
):
    """获取文档的关键词列表"""
    return await get_document_keywords(db, document_id)


@router.delete("/document/{document_id}/{keyword_id}")
async def delete_document_keyword_api(
    document_id: int,
    keyword_id: int,
    db: Session = Depends(get_db),
):
    """删除文档的关键词关联"""
    if await delete_document_keyword(db, document_id, keyword_id):
        return {"message": "Document keyword association deleted"}
    raise HTTPException(
        status_code=404, detail="Document keyword association not found"
    )
