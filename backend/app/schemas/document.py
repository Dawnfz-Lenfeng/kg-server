from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from ..config import settings
from .base import KeywordBrief, SetOperation


class FileType(str, Enum):
    PDF = "pdf"
    TXT = "txt"


class DocStage(str, Enum):
    """文档处理阶段枚举"""

    UPLOAD = "upload"
    EXTRACTED = "is_extracted"
    NORMALIZED = "is_normalized"

    @property
    def storage_dir(self) -> str:
        """获取对应的存储目录"""
        return {
            self.UPLOAD: settings.UPLOAD_DIR,
            self.EXTRACTED: settings.RAW_TEXT_DIR,
            self.NORMALIZED: settings.NORM_TEXT_DIR,
        }[self]


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
    keyword_ids: list[int] | None = Field(default=None, description="关键词ID列表")


class DocUpdate(BaseModel):
    """更新文档请求模型"""

    title: str | None = Field(None, description="文档标题")
    subject_id: int | None = Field(None, description="学科ID")
    keywords: SetOperation | None = Field(None, description="关键词更新操作")


class DocResponse(DocBase):
    """文档响应模型"""

    id: int = Field(..., description="文档ID")
    file_name: str = Field(..., description="文件名称")
    is_extracted: bool = Field(..., description="是否已提取文本")
    is_normalized: bool = Field(..., description="是否已标准化")
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
