from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import transaction
from ..exceptions.keyword import KeywordAlreadyExistsError, KeywordCreationError
from ..models.document import Document
from ..models.keyword import Keyword
from ..schemas.keyword import KeywordCreate, KeywordUpdate


class KeywordService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_keyword(self, keyword_create: KeywordCreate) -> Keyword:
        """创建关键词"""
        existing = await self.read_keyword_by_name(keyword_create.name)
        if existing:
            raise KeywordAlreadyExistsError(
                f"Keyword '{keyword_create.name}' has already been created"
            )

        async with transaction(self.db):
            db_keyword = Keyword(name=keyword_create.name)
            if keyword_create.document_ids:
                stmt = select(Document).where(
                    Document.id.in_(keyword_create.document_ids)
                )
                documents = set((await self.db.execute(stmt)).scalars().all())
                db_keyword.documents = documents

            self.db.add(db_keyword)

        await self.db.refresh(db_keyword)

        keyword = await self.read_keyword(db_keyword.id)
        if keyword is None:
            raise KeywordCreationError("Failed to create keyword")

        return keyword

    async def read_keyword(self, keyword_id: int) -> Keyword | None:
        """获取单个关键词"""
        stmt = (
            select(Keyword)
            .where(Keyword.id == keyword_id)
            .options(selectinload(Keyword.documents))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def read_keyword_by_name(self, name: str) -> Keyword | None:
        """通过名称获取关键词"""
        stmt = (
            select(Keyword)
            .where(Keyword.name == name)
            .options(selectinload(Keyword.documents))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def read_keywords(
        self, skip: int, limit: int, search: str | None
    ) -> Sequence[Keyword]:
        """获取关键词列表"""
        stmt = select(Keyword).options(selectinload(Keyword.documents))
        if search:
            stmt = stmt.where(Keyword.name.ilike(f"%{search}%"))
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_keyword(
        self, keyword_id: int, keyword_update: KeywordUpdate
    ) -> Keyword | None:
        """更新关键词"""
        db_keyword = await self.read_keyword(keyword_id)
        if db_keyword is None:
            return None

        async with transaction(self.db):
            if keyword_update.name and keyword_update.name != db_keyword.name:
                existing = await self.read_keyword_by_name(keyword_update.name)
                if existing:
                    raise KeywordAlreadyExistsError(
                        f"Keyword '{keyword_update.name}' has already been created"
                    )
                db_keyword.name = keyword_update.name

            if keyword_update.documents is not None:
                if keyword_update.documents.add:
                    stmt = select(Document).where(
                        Document.id.in_(keyword_update.documents.add)
                    )
                    docs_to_add = set((await self.db.execute(stmt)).scalars().all())
                    db_keyword.documents |= docs_to_add

                if keyword_update.documents.remove:
                    stmt = select(Document).where(
                        Document.id.in_(keyword_update.documents.remove)
                    )
                    docs_to_remove = set((await self.db.execute(stmt)).scalars().all())
                    db_keyword.documents -= docs_to_remove

            self.db.add(db_keyword)

        return await self.read_keyword(keyword_id)

    async def delete_keyword(self, keyword_id: int) -> bool:
        """删除关键词"""
        db_keyword = await self.read_keyword(keyword_id)
        if db_keyword is None:
            return False

        async with transaction(self.db):
            await self.db.delete(db_keyword)
        return True
