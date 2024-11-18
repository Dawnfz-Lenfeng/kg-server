from typing import Optional

from pydantic import BaseModel, Field


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


class DocumentKeywordBase(BaseModel):
    """文档关键词关联基础模型"""

    keyword_id: int
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class DocumentKeywordCreate(DocumentKeywordBase):
    """创建文档关键词关联请求模型"""

    pass


class DocumentKeywordResponse(DocumentKeywordBase):
    """文档关键词关联响应模型"""

    document_id: int
    keyword: KeywordResponse

    class Config:
        from_attributes = True
