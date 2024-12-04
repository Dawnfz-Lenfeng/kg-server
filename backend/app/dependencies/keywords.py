from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.keyword import KeywordService


async def get_kw_svc(db: AsyncSession = Depends(get_db)):
    return KeywordService(db)
