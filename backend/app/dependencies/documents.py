import asyncio
import os
import uuid
from pathlib import Path
from typing import cast

from fastapi import Depends, File, Form, HTTPException, UploadFile

from ..config import settings
from ..database import get_db
from ..schemas.document import DocCreate, FileType
from ..services.document import DocService


def get_doc_svc(db=Depends(get_db)):
    return DocService(db)


async def get_doc(
    file: UploadFile = File(...),
    subject_id: int = Form(...),
    title: str | None = Form(None),
    file_type: FileType | None = Form(None),
    keyword_ids: list[int] | None = Form(None),
) -> DocCreate:
    """解析文档上传的表单数据"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    suffix = Path(file.filename).suffix[1:]
    return DocCreate(
        title=title or Path(file.filename).stem,
        file_name=await _save_uploaded_file(file),
        file_type=file_type or FileType(suffix),
        subject_id=subject_id,
        keyword_ids=keyword_ids,
    )


async def get_docs(
    files: list[UploadFile] = File(...),
    subject_id: int = Form(...),
    titles: list[str] | None = Form(None),
    file_types: list[FileType] | None = Form(None),
) -> list[DocCreate]:
    """批量处理文档上传"""
    if titles is not None and len(files) != len(titles):
        raise HTTPException(status_code=400, detail="File and title count mismatch")

    if file_types is not None and len(files) != len(file_types):
        raise HTTPException(status_code=400, detail="File and file type count mismatch")

    tasks = [
        get_doc(
            file=file,
            title=titles[i] if titles is not None else None,
            file_type=file_types[i] if file_types is not None else None,
            subject_id=subject_id,
            keyword_ids=None,
        )
        for i, file in enumerate(files)
    ]

    return await asyncio.gather(*tasks)


async def _save_uploaded_file(file: UploadFile) -> str:
    """保存上传的文件到指定目录"""
    file_name = _get_unique_filename(cast(str, file.filename))
    file_path = os.path.join(settings.UPLOAD_DIR, file_name)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return file_name


def _get_unique_filename(original_name: str) -> str:
    """生成唯一文件名 - 私有辅助方法"""
    stem = Path(original_name).stem
    suffix = Path(original_name).suffix
    return f"{stem}_{uuid.uuid4().hex[:8]}{suffix}"
