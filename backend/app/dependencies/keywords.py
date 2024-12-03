from fastapi import Depends

from ..database import get_db
from ..services.keyword import KeywordService


async def get_kw_svc(db=Depends(get_db)):
    return KeywordService(db)
