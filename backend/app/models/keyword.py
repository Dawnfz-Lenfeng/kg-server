from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from ..database import Base

# 定义关联表
document_keywords = Table(
    "document_keywords",
    Base.metadata,
    Column("document_id", ForeignKey("documents.id"), primary_key=True),
    Column("keyword_id", ForeignKey("keywords.id"), primary_key=True),
    Column("weight", Float, nullable=False, default=1.0),
)


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    documents = relationship(
        "Document",
        secondary=document_keywords,  # 使用 Table 对象
        back_populates="keywords"
    )
