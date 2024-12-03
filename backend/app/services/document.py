import os
from contextlib import asynccontextmanager
from typing import Sequence

import aiofiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import transaction
from ..models import Document, Keyword
from ..preprocessing import extract_text, normalize_text
from ..schemas.document import DocCreate, DocStage, DocUpdate
from ..schemas.preprocessing import ExtractConfig, NormalizeConfig


class DocService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_doc(self, doc: DocCreate) -> Document:
        """创建文档"""
        db_doc = Document(**doc.model_dump(exclude={"keyword_ids"}, exclude_unset=True))
        try:
            async with transaction(self.db):
                if doc.keyword_ids:
                    stmt = select(Keyword).where(Keyword.id.in_(doc.keyword_ids))
                    keywords = set((await self.db.execute(stmt)).scalars().all())
                    db_doc.keywords = keywords

                self.db.add(db_doc)

            await self.db.refresh(db_doc)
            return db_doc
        except Exception as e:
            file_path = db_doc.upload_path
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e

    async def extract_doc_text(
        self, doc_id: int, extract_config: ExtractConfig
    ) -> Document | None:
        """提取文档文本"""
        doc = await self.read_doc(doc_id)
        if doc is None:
            return None

        text = extract_text(
            doc.upload_path,
            file_type=doc.file_type,
            **extract_config.model_dump(),
        )

        async with self._write_text(doc, DocStage.EXTRACTED) as f:
            await f.write(text)

        async with transaction(self.db):
            self.db.add(doc)

        await self.db.refresh(doc)
        return doc

    async def normalize_doc_text(
        self, doc_id: int, normalize_config: NormalizeConfig
    ) -> Document | None:
        """标准化文档文本"""
        doc = await self.read_doc(doc_id)
        if doc is None or not doc.is_extracted:
            return None

        async with aiofiles.open(doc.extracted_path, "r", encoding="utf-8") as f:
            raw_text = await f.read()

        normalized_text = normalize_text(
            raw_text,
            **normalize_config.model_dump(),
        )

        async with self._write_text(doc, DocStage.NORMALIZED) as f:
            await f.write(normalized_text)

        async with transaction(self.db):
            self.db.add(doc)

        await self.db.refresh(doc)
        return doc

    async def update_doc(self, doc_id: int, doc_update: DocUpdate) -> Document | None:
        """更新文档信息"""
        doc = await self.read_doc(doc_id)
        if doc is None:
            return None

        async with transaction(self.db):
            update_data = doc_update.model_dump(
                exclude={"keywords"}, exclude_unset=True
            )
            for key, value in update_data.items():
                setattr(doc, key, value)

            if doc_update.keywords is not None:
                keywords_update = doc_update.keywords

                if keywords_update.add:
                    stmt = select(Keyword).where(Keyword.id.in_(keywords_update.add))
                    keywords_to_add = set((await self.db.execute(stmt)).scalars().all())
                    doc.keywords |= keywords_to_add

                if keywords_update.remove:
                    stmt = select(Keyword).where(Keyword.id.in_(keywords_update.remove))
                    keywords_to_remove = set(
                        (await self.db.execute(stmt)).scalars().all()
                    )
                    doc.keywords -= keywords_to_remove

            self.db.add(doc)

        await self.db.refresh(doc)
        return doc

    async def read_doc(self, doc_id: int) -> Document | None:
        """获取单个文档"""
        stmt = (
            select(Document)
            .where(Document.id == doc_id)
            .options(selectinload(Document.keywords))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def read_docs(
        self, skip: int, limit: int, subject_id: int | None
    ) -> Sequence[Document]:
        """获取文档列表"""
        stmt = select(Document).options(selectinload(Document.keywords))
        if subject_id is not None:
            stmt = stmt.where(Document.subject_id == subject_id)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def read_doc_text(self, doc_id: int, stage: DocStage) -> str | None:
        """获取文档文本内容"""
        doc = await self.read_doc(doc_id)
        if doc is None:
            return None

        if not getattr(doc, stage):
            return None

        async with aiofiles.open(doc.get_path(stage), "r", encoding="utf-8") as f:
            return await f.read()

    async def delete_doc(self, doc_id: int) -> bool:
        """删除文档"""
        doc = await self.read_doc(doc_id)
        if doc is None:
            return False

        for stage in list(DocStage):
            file_path = doc.get_path(stage)
            if os.path.exists(file_path):
                os.remove(file_path)

        async with transaction(self.db):
            await self.db.delete(doc)
        return True

    @asynccontextmanager
    async def _write_text(self, doc: Document, stage: DocStage):
        """文本处理上下文管理器"""
        if not getattr(doc, stage):
            setattr(doc, stage, True)

        file = None
        try:
            file_path = doc.get_path(stage)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file = await aiofiles.open(file_path, "w", encoding="utf-8")
            yield file

        finally:
            if file is not None:
                await file.close()
                if stage == DocStage.NORMALIZED:
                    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                        text = await f.read()
                        doc.word_count = len(text)
