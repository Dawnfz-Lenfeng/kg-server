from enum import Enum
from typing import Optional
from pydantic import BaseModel


class SubjectType(str, Enum):
    """学科类型枚举"""

    FINANCE = "finance"  # 金融
    ECONOMICS = "economics"  # 经济
    STATISTICS = "statistics"  # 统计
    DATA_SCIENCE = "data_science"  # 数据科学
    OTHER = "other"  # 其他


class SubjectBase(BaseModel):
    """主题基础模型"""

    name: str
    type: SubjectType
    description: Optional[str] = None


class SubjectCreate(SubjectBase):
    """创建主题请求模型"""

    pass


class SubjectResponse(SubjectBase):
    """主题响应模型"""

    id: int

    class Config:
        from_attributes = True
