from io import BytesIO, StringIO

import pandas as pd
from fastapi import Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.keyword import KeywordCreate
from ..services import DocKeywordService, KeywordService


async def get_kw_svc(db: AsyncSession = Depends(get_db)):
    return KeywordService(db)


async def get_doc_kw_svc(db: AsyncSession = Depends(get_db)):
    return DocKeywordService(db)


async def get_keywords(
    file: UploadFile = File(...),
) -> list[KeywordCreate]:
    """从上传的文件中读取关键词列表"""
    assert file.filename, "文件名不能为空"

    content = await file.read()

    file_type = file.filename.rsplit(".", 1)[-1].lower()
    match file_type:
        case "csv":
            df = pd.read_csv(StringIO(content.decode()), header=None)
        case "xlsx":
            df = pd.read_excel(BytesIO(content), header=None)
        case _:
            raise ValueError("不支持的文件类型")

    if df.shape[1] < 2:
        raise ValueError("文件必须至少包含两列")

    keywords = [KeywordCreate(name=row[0], subject=row[1]) for _, row in df.iterrows()]

    return keywords
