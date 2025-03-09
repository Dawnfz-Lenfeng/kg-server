from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from .base import KeywordBrief

if TYPE_CHECKING:
    from ..models import Document


class FileType(str, Enum):
    PDF = "pdf"
    TXT = "txt"


class DocState(str, Enum):
    """文档处理状态"""

    # 已完成状态
    UPLOADED = "uploaded"  # 已上传
    EXTRACTED = "extracted"  # 已提取
    NORMALIZED = "normalized"  # 已标准化
    # 处理中状态
    EXTRACTING = "extracting"  # 提取中
    NORMALIZING = "normalizing"  # 标准化中

    def __lt__(self, other: str) -> bool:
        """状态比较：用于判断处理进度"""
        order = [
            self.UPLOADED,
            self.EXTRACTING,
            self.EXTRACTED,
            self.NORMALIZING,
            self.NORMALIZED,
        ]
        return order.index(self) < order.index(other)

    @property
    def is_finished(self) -> bool:
        """是否是完成状态"""
        return self in {self.UPLOADED, self.EXTRACTED, self.NORMALIZED}

    @property
    def is_processing(self) -> bool:
        """是否是处理中状态"""
        return self in {self.EXTRACTING, self.NORMALIZING}


class DocBase(BaseModel):
    """文档基础模型"""

    title: str = Field(..., description="文档标题")
    file_type: FileType = Field(FileType.PDF, description="文件类型 (pdf, txt)")


class DocCreate(DocBase):
    """创建文档请求模型"""

    local_file_name: str = Field(..., description="文件名称")


class DocUpdate(BaseModel):
    """更新文档请求模型"""

    title: str | None = Field(None, description="文档标题")


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


class FileUploadResult(BaseModel):
    """文件上传结果 - 匹配前端 UploadApiResult"""

    code: int = Field(200, description="响应码")
    message: str = Field("上传成功", description="响应信息")
    url: str = Field(..., description="文件访问路径")
    fileName: str = Field(..., description="文件名")


class DocItem(BaseModel):
    """文档列表项"""

    id: int = Field(..., description="文档ID")
    fileName: str = Field(..., description="文件名")
    fileSize: int = Field(..., description="文件大小")
    uploadTime: str = Field(..., description="上传时间")
    updateTime: str = Field(..., description="最后更新时间")
    url: str = Field(..., description="下载链接")
    state: str = Field(..., description="文档状态")

    @classmethod
    def from_doc(cls, doc: Document):
        """从文档数据创建列表项"""
        return cls(
            id=doc.id,
            fileName=doc.file_name,
            fileSize=doc.file_size,
            uploadTime=doc.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updateTime=doc.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            url=doc.url,
            state=doc.state.value,
        )


class DocList(BaseModel):
    """文档列表响应"""

    items: list[DocItem] = Field(..., description="文档列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    pageSize: int = Field(..., description="每页数量")
