from io import StringIO, BytesIO

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

    file_type = file.filename.split(".")[-1]
    match file_type:
        case "csv":
            df = pd.read_csv(StringIO(content.decode()))
        case "xlsx":
            df = pd.read_excel(BytesIO(content))
        case _:
            raise ValueError("不支持的文件类型")

    if "keyword" not in df.columns or "subject" not in df.columns:
        raise ValueError("文件必须包含 'keyword' 和 'subject' 列")

    keywords = [
        KeywordCreate(name=row["keyword"], subject=row["subject"])
        for _, row in df.iterrows()
    ]

    return keywords
