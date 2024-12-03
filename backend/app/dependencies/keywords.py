from ..services.keyword import KeywordService
from ..database import get_db
from fastapi import Depends


def get_kw_svc(db=Depends(get_db)):
    return KeywordService(db)
