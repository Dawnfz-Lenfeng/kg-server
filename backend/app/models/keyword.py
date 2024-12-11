from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .document import Document

# 定义关联表
document_keywords = Table(
    "document_keywords",
    Base.metadata,
    Column("document_id", ForeignKey("documents.id"), primary_key=True),
    Column("keyword_id", ForeignKey("keywords.id"), primary_key=True),
)


class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    documents: Mapped[set[Document]] = relationship(
        "Document",
        secondary="document_keywords",
        collection_class=set,
        back_populates="keywords",
        lazy="selectin",
    )

    @property
    def doc_count(self) -> int:
        """获取使用该关键词的文档数量"""
        return len(self.documents)
