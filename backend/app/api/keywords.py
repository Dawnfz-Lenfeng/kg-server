from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from ..dependencies.keywords import get_doc_kw_svc, get_kw_svc
from ..exceptions.keyword import KeywordAlreadyExistsError, KeywordCreationError
from ..schemas.document import DocResponse
from ..schemas.keyword import (
    KeywordCreate,
    KeywordDetailResponse,
    KeywordResponse,
    KeywordUpdate,
)
from ..services import DocKeywordService, KeywordService

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.post("", response_model=KeywordDetailResponse)
async def create_keyword(
    keyword: KeywordCreate,
    kw_svc: KeywordService = Depends(get_kw_svc),
):
    """创建关键词"""
    try:
        return await kw_svc.create_keyword(keyword)
    except KeywordAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeywordCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{doc_id}", response_model=DocResponse)
async def create_keywords_for_doc(
    doc_id: int,
    file: UploadFile = File(...),
    doc_kw_svc: DocKeywordService = Depends(get_doc_kw_svc),
):
    """创建关键词并关联到文档"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")

    try:
        content = (await file.read()).decode("utf-8")
        keywords = [line.strip() for line in content.splitlines() if line.strip()]

        doc = await doc_kw_svc.create_keywards_for_doc(doc_id, keywords)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")

        return doc
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")


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
