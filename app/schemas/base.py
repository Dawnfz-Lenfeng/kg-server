from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResultEnum(Enum):
    SUCCESS = 0
    ERROR = 1
    TIMEOUT = 401


class Result(BaseModel, Generic[T]):
    """通用响应模型"""

    code: int = Field(default=ResultEnum.SUCCESS.value, description="响应码")
    message: str | None = Field(default=None, description="响应信息")
    result: T | None = Field(default=None, description="响应数据")


class Page(BaseModel, Generic[T]):
    """通用分页响应模型"""

    items: list[T] = Field(..., description="列表内容")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    pageSize: int = Field(..., description="每页数量")
