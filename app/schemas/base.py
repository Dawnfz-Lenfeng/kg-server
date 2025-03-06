from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ResultEnum(Enum):
    SUCCESS = 0
    ERROR = 1
    TIMEOUT = 401


class Result(BaseModel, Generic[T]):
    """通用响应模型"""

    code: ResultEnum = Field(default=ResultEnum.SUCCESS, description="响应码")
    message: str | None = Field(default=None, description="响应信息")
    result: T | None = Field(default=None, description="响应数据")

    model_config = ConfigDict(arbitrary_types_allowed=True)


class DocBrief(BaseModel):
    """文档简要信息（用于关联展示）"""

    id: int = Field(..., description="文档ID")
    title: str = Field(..., description="文档标题")

    model_config = ConfigDict(from_attributes=True)


class KeywordBrief(BaseModel):
    """关键词简要信息（用于关联展示）"""

    id: int = Field(..., description="关键词ID")
    name: str = Field(..., description="关键词名称")

    model_config = ConfigDict(from_attributes=True)
