import uuid
from pathlib import Path
from typing import cast

from fastapi import Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.document import DocCreate, FileType
from ..services.document import DocService
from ..settings import settings


async def get_doc_svc(db: AsyncSession = Depends(get_db)) -> DocService:
    return DocService(db)


async def get_doc(
    file: UploadFile = File(...),
    title: str = Form(...),
) -> DocCreate:
    """解析文档上传的表单数据

    Args:
        file: 上传的文件
        title: 文档标题
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    file_type = file.filename.split(".")[-1]

    try:
        file_type = FileType(file_type)
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type: {file_type}"
        )

    # 保存文件并创建文档
    saved_filename = await _save_uploaded_file(file)

    return DocCreate(
        title=title,
        local_file_name=saved_filename,
        file_type=file_type,
    )


async def _save_uploaded_file(file: UploadFile):
    """保存上传的文件到指定目录"""
    file_name = _get_unique_filename(cast(str, file.filename))
    file_path = settings.UPLOAD_DIR / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)

    content = await file.read()
    file_path.write_bytes(content)

    return file_path.stem


def _get_unique_filename(original_name: str):
    """生成唯一文件名 - 私有辅助方法"""
    path = Path(original_name)
    return Path(f"{path.stem}_{uuid.uuid4().hex[:8]}{path.suffix}")
