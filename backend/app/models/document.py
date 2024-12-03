from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..config import settings
from ..database import Base
from ..schemas.document import DocStage
from .keyword import document_keywords

if TYPE_CHECKING:
    from .keyword import Keyword
    from .subject import Subject


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    file_name: Mapped[str] = mapped_column(nullable=False)
    file_type: Mapped[str] = mapped_column(nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    is_extracted: Mapped[bool] = mapped_column(default=False)
    is_normalized: Mapped[bool] = mapped_column(default=False)
    word_count: Mapped[int | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now, nullable=False
    )

    subject: Mapped[Subject] = relationship(back_populates="documents")
    keywords: Mapped[set[Keyword]] = relationship(
        "Keyword",
        secondary=document_keywords,
        collection_class=set,
        back_populates="documents",
    )

    @property
    def upload_path(self) -> str:
        """获取原始上传文件路径"""
        return f"{settings.UPLOAD_DIR}/{self.file_name}"

    @property
    def extracted_path(self) -> str:
        """获取提取文本的文件路径"""
        return f"{settings.RAW_TEXT_DIR}/{self.file_name}"

    @property
    def normalized_path(self) -> str:
        """获取标准化文本的文件路径"""
        return f"{settings.NORM_TEXT_DIR}/{self.file_name}"

    def get_path(self, stage: DocStage) -> str:
        """根据处理阶段获取对应的文件路径"""
        return {
            DocStage.UPLOAD: self.upload_path,
            DocStage.EXTRACTED: self.extracted_path,
            DocStage.NORMALIZED: self.normalized_path,
        }[stage]
