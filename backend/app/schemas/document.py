from enum import Enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .base import KeywordBrief, SetOperation


class FileType(str, Enum):
    PDF = "pdf"
    TXT = "txt"


class DocBase(BaseModel):
    """文档基础模型"""

    title: str = Field(..., description="文档标题")
    file_type: FileType = Field(FileType.PDF, description="文件类型 (pdf, txt)")
    subject_id: int = Field(
        ..., description="学科ID (1=金融, 2=经济, 3=统计, 4=数据科学)", ge=1
    )


class DocCreate(BaseModel):
    """创建文档请求模型"""

    subject_id: int = Field(
        ..., description="学科ID (1=金融, 2=经济, 3=统计, 4=数据科学)", ge=1
    )
    title: str | None = Field(None, description="文档标题")
    file_type: FileType | None = Field(None, description="文件类型 (pdf, txt)")
    keyword_ids: list[int] | None = Field(default=None, description="关键词ID列表", examples=[[1, 2]])


class DocUpdate(BaseModel):
    """更新文档请求模型"""

    title: str | None = Field(None, description="文档标题")
    subject_id: int | None = Field(None, description="学科ID")
    keywords: SetOperation | None = Field(None, description="关键词更新操作")


class DocResponse(DocBase):
    """文档响应基础模型"""

    id: int = Field(..., description="文档ID")
    keywords: list[KeywordBrief] = Field(default_factory=list, description="关键词列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime | None = Field(None, description="最后更新时间")

    model_config = ConfigDict(from_attributes=True, json_encoders={set: list})


class DocDetailResponse(DocResponse):
    """文档详细响应模型"""

    file_path: str = Field(..., description="文件路径")
    origin_text: str | None = Field(None, description="原始文本内容")
    processed_text: str | None = Field(None, description="处理后的文本内容")
