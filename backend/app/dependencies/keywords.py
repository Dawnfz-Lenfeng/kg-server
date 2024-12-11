from fastapi import Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services import DocKeywordService, KeywordService


async def get_kw_svc(db: AsyncSession = Depends(get_db)):
    return KeywordService(db)


async def get_doc_kw_svc(db: AsyncSession = Depends(get_db)):
    return DocKeywordService(db)


async def get_keywords(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")

    content = (await file.read()).decode("utf-8")
    keywords = [line.strip() for line in content.splitlines() if line.strip()]

    return keywords
