from __future__ import annotations

import os
from datetime import datetime
from typing import TYPE_CHECKING

import aiofiles
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..config import settings
from ..database import Base
from ..schemas.document import DocState, FileType
from .keyword import document_keywords

if TYPE_CHECKING:
    from .keyword import Keyword
    from .subject import Subject


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    file_name: Mapped[str] = mapped_column(nullable=False)
    file_type: Mapped[FileType] = mapped_column(nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    state: Mapped[DocState] = mapped_column(default=DocState.UPLOADED, nullable=False)
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

    def get_path(self, stage: DocState) -> str:
        """根据处理阶段获取对应的文件路径"""
        return {
            DocState.UPLOADED: self.upload_path,
            DocState.EXTRACTED: self.extracted_path,
            DocState.NORMALIZED: self.normalized_path,
        }[stage]

    def create_dirs(self):
        """创建文档所需的所有目录"""
        for stage in DocState:
            file_path = self.get_path(stage)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

    def delete_dirs(self):
        """删除文档所需的所有目录"""
        for stage in DocState:
            file_path = self.get_path(stage)
            if os.path.exists(file_path):
                os.remove(file_path)

    async def read_text(self, stage: DocState) -> str:
        """读取文档文本"""
        file_path = self.get_path(stage)
        async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
            return await file.read()

    async def write_text(self, text: str, stage: DocState):
        """写入文档文本并更新状态"""
        if self.state < stage:
            self.state = stage

        file_path = self.get_path(stage)
        async with aiofiles.open(file_path, "w", encoding="utf-8") as file:
            await file.write(text)

        if stage == DocState.NORMALIZED:
            self.word_count = len(text)
