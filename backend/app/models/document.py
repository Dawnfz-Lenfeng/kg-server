from __future__ import annotations

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
    def upload_path(self):
        """获取原始上传文件路径"""
        return settings.UPLOAD_DIR / f"{self.file_name}.{self.file_type}"

    @property
    def extracted_path(self):
        """获取提取文本的文件路径"""
        return settings.RAW_TEXT_DIR / f"{self.file_name}.txt"

    @property
    def normalized_path(self):
        """获取标准化文本的文件路径"""
        return settings.NORM_TEXT_DIR / f"{self.file_name}.txt"

    def get_path(self, state: DocState):
        """根据处理阶段获取对应的文件路径"""
        return {
            DocState.UPLOADED: self.upload_path,
            DocState.EXTRACTED: self.extracted_path,
            DocState.NORMALIZED: self.normalized_path,
        }[state]

    def create_dirs(self):
        """创建文档所需的所有目录"""
        for state in DocState:
            file_path = self.get_path(state)
            file_path.parent.mkdir(parents=True, exist_ok=True)

    def delete_dirs(self):
        """删除文档所需的所有目录"""
        for state in DocState:
            file_path = self.get_path(state)
            file_path.unlink(missing_ok=True)

    async def read_text(self, state: DocState) -> str:
        """读取文档文本"""
        file_path = self.get_path(state)
        async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
            return await file.read()

    async def write_text(self, text: str, state: DocState):
        """写入文档文本并更新状态"""
        if self.state < state:
            self.state = state

        file_path = self.get_path(state)
        async with aiofiles.open(file_path, "w", encoding="utf-8") as file:
            await file.write(text)

        if state == DocState.NORMALIZED:
            self.word_count = len(text)
