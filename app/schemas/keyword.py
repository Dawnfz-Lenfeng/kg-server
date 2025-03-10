from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

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


class KeywordItem(KeywordBase):
    """关键词列表项模型"""

    id: int = Field(..., description="关键词ID", examples=[1])
    model_config = ConfigDict(from_attributes=True)
