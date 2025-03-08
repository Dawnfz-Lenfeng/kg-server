from datetime import datetime

import aiofiles
from kgtools.preprocessing import extract_text, normalize_text
from kgtools.schemas.preprocessing import ExtractConfig, NormalizeConfig
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import transaction
from ..models import Document
from ..schemas.document import DocCreate, DocItem, DocState, DocUpdate


class DocService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_doc(self, doc_create: DocCreate) -> Document:
        """创建文档"""
        db_doc = Document(**doc_create.model_dump())
        db_doc.create_dirs()
        try:
            async with transaction(self.db):
                self.db.add(db_doc)

            await self.db.refresh(db_doc)
            return db_doc

        except Exception as e:
            db_doc.delete_dirs()
            raise e

    async def extract_doc(self, doc_id: int, config: ExtractConfig):
        """提取文档内容"""
        try:
            doc = await self.get_doc(doc_id)
            if not doc:
                raise ValueError(f"Document {doc_id} not found")

            text = extract_text(
                doc.upload_path,
                file_type=doc.file_type,
                **config.model_dump(),
            )

            async with transaction(self.db):
                await doc.write_text(text, DocState.EXTRACTED)

        except Exception as e:
            await self.update_doc_state(doc_id, DocState.UPLOADED)
            raise e

    async def normalize_doc(self, doc_id: int, config: NormalizeConfig) -> None:
        """标准化文档内容"""
        try:
            doc = await self.get_doc(doc_id)
            if not doc:
                raise ValueError(f"Document {doc_id} not found")

            async with aiofiles.open(doc.extracted_path, "r", encoding="utf-8") as f:
                raw_text = await f.read()

            normalized_text = normalize_text(
                raw_text,
                **config.model_dump(),
            )

            async with transaction(self.db):
                await doc.write_text(normalized_text, DocState.NORMALIZED)

        except Exception as e:
            await self.update_doc_state(doc_id, DocState.EXTRACTED)
            raise e

    async def update_doc(self, doc_id: int, doc_update: DocUpdate) -> Document | None:
        """更新文档信息"""
        doc = await self.get_doc(doc_id)
        if doc is None:
            return None

        async with transaction(self.db):
            update_data = doc_update.model_dump(
                exclude={"keywords"}, exclude_unset=True
            )
            for key, value in update_data.items():
                setattr(doc, key, value)

        await self.db.refresh(doc)
        return doc

    async def update_doc_state(self, doc_id: int, state: DocState):
        """更新文档状态"""
        doc = await self.get_doc(doc_id)
        if doc is None:
            raise ValueError(f"Document {doc_id} not found")

        async with transaction(self.db):
            doc.state = state
            doc.updated_at = datetime.now()

    async def get_doc(self, doc_id: int) -> Document | None:
        """读取文档"""
        result = await self.db.execute(
            select(Document)
            .where(Document.id == doc_id)
            .options(selectinload(Document.keywords))
        )
        return result.scalar_one_or_none()

    async def get_doc_list(self, skip: int = 0, limit: int = 10):
        """获取文档列表"""
        # 获取总数
        result = await self.db.execute(select(func.count(Document.id)))
        total = result.scalar_one()

        # 获取分页数据
        result = await self.db.execute(
            select(Document)
            .offset(skip)
            .limit(limit)
            .order_by(Document.created_at.desc())
        )
        docs = result.scalars().all()
        items = [DocItem.from_doc(doc) for doc in docs]  # type: ignore

        return items, total

    async def download_doc(self, doc_id: int, state: DocState):
        """下载文档"""
        doc = await self.get_doc(doc_id)
        if doc is None:
            raise ValueError(f"Document {doc_id} not found")
        if doc.state < state:
            raise ValueError(f"Document {doc_id} is not in {state} state")

        path = doc.get_path(state)
        filename = (
            doc.file_name if state == DocState.UPLOADED else f"{doc.title}.{state}.txt"
        )

        return path, filename

    async def delete_doc(self, doc_id: int) -> bool:
        """删除文档"""
        doc = await self.get_doc(doc_id)
        if doc is None:
            return False

        doc.delete_dirs()

        async with transaction(self.db):
            await self.db.delete(doc)
        return True
