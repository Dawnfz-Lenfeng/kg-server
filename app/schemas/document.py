from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from .base import KeywordBrief


class FileType(str, Enum):
    PDF = "pdf"
    TXT = "txt"


class DocState(str, Enum):
    """文档处理状态"""

    UPLOADED = "uploaded"
    EXTRACTED = "extracted"
    NORMALIZED = "normalized"

    def __lt__(self, other: str) -> bool:
        """状态比较：用于判断处理进度"""
        order = [self.UPLOADED, self.EXTRACTED, self.NORMALIZED]
        return order.index(self) < order.index(other)


class DocBase(BaseModel):
    """文档基础模型"""

    title: str = Field(..., description="文档标题")
    file_type: FileType = Field(FileType.PDF, description="文件类型 (pdf, txt)")
    subject_id: int = Field(
        ..., description="学科ID (1=金融, 2=经济, 3=统计, 4=数据科学)", ge=1
    )


class DocCreate(DocBase):
    """创建文档请求模型"""

    file_name: str = Field(..., description="文件名称")


class DocUpdate(BaseModel):
    """更新文档请求模型"""

    title: str | None = Field(None, description="文档标题")
    subject_id: int | None = Field(None, description="学科ID")


class DocResponse(DocBase):
    """文档响应模型"""

    id: int = Field(..., description="文档ID")
    file_name: str = Field(..., description="文件名称")
    state: DocState = Field(..., description="文档处理状态")
    word_count: int | None = Field(None, description="文档字数")
    keywords: list[KeywordBrief] = Field(default_factory=list, description="关键词列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime | None = Field(None, description="最后更新时间")

    model_config = ConfigDict(from_attributes=True, json_encoders={set: list})


class DocUploadResult(BaseModel):
    """文档上传结果"""

    success: bool = Field(..., description="是否上传成功")
    document: DocResponse | None = Field(None, description="文档详情")
    error: str | None = Field(None, description="错误信息")

    model_config = ConfigDict(from_attributes=True)
