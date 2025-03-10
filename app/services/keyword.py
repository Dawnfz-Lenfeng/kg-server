from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import transaction
from ..models.keyword import Keyword
from ..schemas.keyword import KeywordCreate, KeywordItem, KeywordUpdate


class KeywordService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_keyword(self, keyword_create: KeywordCreate):
        """创建关键词"""
        if await self.read_keyword_by_name(keyword_create.name):
            raise ValueError(
                f"Keyword '{keyword_create.name}' has already been created"
            )

        async with transaction(self.db):
            db_keyword = Keyword(**keyword_create.model_dump())
            self.db.add(db_keyword)

    async def read_keyword(self, keyword_id: int):
        """获取单个关键词"""
        result = await self.db.execute(select(Keyword).where(Keyword.id == keyword_id))
        return result.scalar_one_or_none()

    async def read_keyword_by_name(self, name: str):
        """通过名称获取关键词"""
        result = await self.db.execute(select(Keyword).where(Keyword.name == name))
        return result.scalar_one_or_none()

    async def get_keyword_list(self, skip: int = 0, limit: int = 10):
        """获取所有关键词"""
        result = await self.db.execute(select(func.count(Keyword.id)))
        total = result.scalar_one()

        result = await self.db.execute(select(Keyword).offset(skip).limit(limit))
        kws = result.scalars().all()
        items = [KeywordItem.model_validate(kw) for kw in kws]

        return items, total

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
                    raise ValueError(
                        f"Keyword '{keyword_update.name}' has already been created"
                    )
                db_keyword.name = keyword_update.name

            self.db.add(db_keyword)

        await self.db.refresh(db_keyword)
        return db_keyword

    async def delete_keyword(self, keyword_id: int) -> bool:
        """删除关键词"""
        db_keyword = await self.read_keyword(keyword_id)
        if db_keyword is None:
            return False

        async with transaction(self.db):
            await self.db.delete(db_keyword)
        return True

    async def delete_keyword_by_name(self, name: str):
        """通过名称删除关键词"""
        db_keyword = await self.read_keyword_by_name(name)
        if db_keyword is None:
            return False

        async with transaction(self.db):
            await self.db.delete(db_keyword)
        return True
