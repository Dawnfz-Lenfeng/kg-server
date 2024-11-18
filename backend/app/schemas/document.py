from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """文档基础模型"""

    title: str = Field(..., description="文档标题")
    file_type: str = Field(..., description="文件类型 (pdf, txt)")
    subject_id: Optional[int] = Field(
        None, description="学科ID (1=金融, 2=经济, 3=统计, 4=数据科学)"
    )


class DocumentCreate(DocumentBase):
    """创建文档请求模型"""

    pass


class DocumentUpdate(BaseModel):
    """更新文档请求模型"""

    title: Optional[str] = Field(None, description="文档标题")
    subject_id: Optional[int] = Field(
        None, description="学科ID (1=金融, 2=经济, 3=统计, 4=数据科学)"
    )


class DocumentListResponse(DocumentBase):
    """文档列表响应模型"""

    id: int = Field(..., description="文档ID")
    file_path: str = Field(..., description="文件路径")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class DocumentResponse(DocumentListResponse):
    """完整文档响应模型"""

    processed_text: Optional[str] = Field(None, description="处理后的文本内容")
    origin_text: Optional[str] = Field(None, description="原始文本内容")
