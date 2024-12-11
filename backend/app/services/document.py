from typing import Sequence

import aiofiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import transaction
from ..models import Document
from ..preprocessing import extract_text, normalize_text
from ..schemas.document import DocCreate, DocState, DocUpdate
from ..schemas.preprocessing import ExtractConfig, NormalizeConfig


class DocService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_doc(self, doc_create: DocCreate) -> Document:
        """创建文档"""
        db_doc = Document(
            **doc_create.model_dump(exclude={"keyword_ids"}, exclude_unset=True)
        )
        db_doc.create_dirs()
        try:
            async with transaction(self.db):
                self.db.add(db_doc)

            await self.db.refresh(db_doc)

            doc = await self.read_doc(db_doc.id)
            if doc is None:
                raise Exception("Create doc failed.")

            return doc

        except Exception as e:
            file_path = db_doc.upload_path
            file_path.unlink(missing_ok=True)
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

        async with transaction(self.db):
            await doc.write_text(text, DocState.EXTRACTED)

        return await self.read_doc(doc_id)

    async def normalize_doc_text(
        self, doc_id: int, normalize_config: NormalizeConfig
    ) -> Document | None:
        """标准化文档文本"""
        doc = await self.read_doc(doc_id)
        if doc is None or doc.state < DocState.EXTRACTED:
            return None

        async with aiofiles.open(doc.extracted_path, "r", encoding="utf-8") as f:
            raw_text = await f.read()

        normalized_text = normalize_text(
            raw_text,
            **normalize_config.model_dump(),
        )

        async with transaction(self.db):
            await doc.write_text(normalized_text, DocState.NORMALIZED)

        return await self.read_doc(doc_id)

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

        return await self.read_doc(doc_id)

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

    async def read_doc_text(self, doc_id: int, state: DocState) -> str | None:
        """获取文档文本内容"""
        doc = await self.read_doc(doc_id)
        if doc is None:
            return None

        if doc.state < state:
            return None

        return await doc.read_text(state)

    async def delete_doc(self, doc_id: int) -> bool:
        """删除文档"""
        doc = await self.read_doc(doc_id)
        if doc is None:
            return False

        doc.delete_dirs()

        async with transaction(self.db):
            await self.db.delete(doc)
        return True
