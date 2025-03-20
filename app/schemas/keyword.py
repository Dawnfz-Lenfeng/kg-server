from pydantic import BaseModel, ConfigDict, Field

from .subject import Subject


class KeywordBase(BaseModel):
    """关键词基础模型"""

    name: str = Field(..., description="关键词名称", examples=["机器学习"])
    subject: Subject = Field(..., description="所属学科")


class KeywordCreate(KeywordBase):
    """创建关键词请求模型"""


class KeywordItem(KeywordBase):
    """关键词列表项模型"""

    id: int = Field(..., description="关键词ID", examples=[1])
    model_config = ConfigDict(from_attributes=True)
