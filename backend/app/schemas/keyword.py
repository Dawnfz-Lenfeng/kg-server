from pydantic import BaseModel, ConfigDict


class KeywordBase(BaseModel):
    """关键词基础模型"""

    name: str


class KeywordCreate(KeywordBase):
    """创建关键词请求模型"""

    pass


class KeywordResponse(KeywordBase):
    """关键词响应模型"""

    id: int

    class Config:
        from_attributes = True


class DocumentKeywordCreate(BaseModel):
    """创建文档关键词关联请求模型"""

    keyword_id: int


class DocumentKeywordResponse(BaseModel):
    """文档关键词关联响应模型"""

    document_id: int
    keyword: KeywordResponse

    model_config = ConfigDict(from_attributes=True)
