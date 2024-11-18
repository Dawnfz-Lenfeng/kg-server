from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DocumentBase(BaseModel):
    """文档基础模型"""

    title: str
    file_type: str
    subject_id: Optional[int] = None


class DocumentCreate(DocumentBase):
    """创建文档请求模型"""

    pass


class DocumentUpdate(BaseModel):
    """更新文档请求模型"""

    title: Optional[str] = None
    subject_id: Optional[int] = None


class DocumentResponse(DocumentBase):
    """文档响应模型"""

    id: int
    file_path: str
    processed_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
