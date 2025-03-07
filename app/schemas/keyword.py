from pydantic import BaseModel, ConfigDict, Field

from .base import DocBrief
from .subject import Subject


class KeywordBase(BaseModel):
    """关键词基础模型"""

    name: str = Field(..., description="关键词名称", examples=["机器学习"])
    subject: Subject = Field(..., description="所属学科")


class KeywordCreate(KeywordBase):
    """创建关键词请求模型"""


class KeywordUpdate(BaseModel):
    """更新关键词请求模型"""

    name: str | None = Field(None, description="关键词名称", examples=["深度学习"])


class KeywordResponse(BaseModel):
    """关键词响应模型"""

    id: int = Field(..., description="关键词ID")
    name: str = Field(..., description="关键词名称")
    doc_count: int = Field(..., description="使用该关键词的文档数量")

    model_config = ConfigDict(from_attributes=True)


class KeywordDetailResponse(KeywordResponse):
    """关键词详细响应模型"""

    documents: list[DocBrief] = Field(
        default_factory=list, description="包含该关键词的文档列表"
    )

    model_config = ConfigDict(from_attributes=True, json_encoders={set: list})
