from enum import IntEnum
from typing import Optional

from pydantic import BaseModel


class SubjectId(IntEnum):
    """学科ID枚举"""

    FINANCE = 1  # 金融
    ECONOMICS = 2  # 经济
    STATISTICS = 3  # 统计
    DATA_SCIENCE = 4  # 数据科学


class SubjectBase(BaseModel):
    """主题基础模型"""

    name: str
    description: Optional[str] = None


class SubjectCreate(SubjectBase):
    """创建主题请求模型"""

    id: SubjectId


class SubjectResponse(SubjectBase):
    """主题响应模型"""

    id: SubjectId

    class Config:
        from_attributes = True
