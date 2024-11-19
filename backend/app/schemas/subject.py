from pydantic import BaseModel


class SubjectBase(BaseModel):
    """主题基础模型"""

    name: str
    description: str | None = None


class SubjectCreate(SubjectBase):
    """创建主题请求模型"""

    id: int


class SubjectResponse(SubjectBase):
    """主题响应模型"""

    id: int

    class Config:
        from_attributes = True
