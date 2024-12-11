from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services import DocKeywordService, KeywordService


async def get_kw_svc(db: AsyncSession = Depends(get_db)):
    return KeywordService(db)


async def get_doc_kw_svc(db: AsyncSession = Depends(get_db)):
    return DocKeywordService(db)
