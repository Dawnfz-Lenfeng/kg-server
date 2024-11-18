from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from ..database import Base

# 定义关联表
document_keywords = Table(
    "document_keywords",
    Base.metadata,
    Column("document_id", ForeignKey("documents.id"), primary_key=True),
    Column("keyword_id", ForeignKey("keywords.id"), primary_key=True),
)


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    documents = relationship(
        "Document",
        secondary=document_keywords,
        back_populates="keywords",
    )
