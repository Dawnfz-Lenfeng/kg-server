from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
        assert isinstance(other, DocState)
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


class FileUploadResult(BaseModel):
    """文件上传结果 - 匹配前端 UploadApiResult"""

    code: int = Field(200, description="响应码")
    message: str = Field("上传成功", description="响应信息")
    url: str = Field(..., description="文件访问路径")
    fileName: str = Field(..., description="文件名")


class DocItem(BaseModel):
    """文档列表项"""

    id: int = Field(..., description="文档ID")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    created_at: str = Field(..., description="上传时间")
    updated_at: str = Field(..., description="最后更新时间")
    url: str = Field(..., description="下载链接")
    state: str = Field(..., description="文档状态")

    model_config = ConfigDict(
        from_attributes=True,
    )

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def convert_datetime_to_str(cls, v):
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M:%S")
        return v
