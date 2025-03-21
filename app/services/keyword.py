from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import transaction
from ..models.keyword import Keyword
from ..schemas.keyword import KeywordCreate, KeywordItem
from ..schemas.subject import Subject


class KeywordService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_keyword(self, keyword_create: KeywordCreate):
        """创建关键词"""
        if await self.get_keyword_by_name(keyword_create.name):
            raise ValueError(
                f"Keyword '{keyword_create.name}' has already been created"
            )

        async with transaction(self.db):
            db_keyword = Keyword(**keyword_create.model_dump())
            self.db.add(db_keyword)

    async def create_keywords(self, keywords: list[KeywordCreate]):
        """批量创建关键词"""
        unique_keywords = {kw.name: kw for kw in keywords}
        if not unique_keywords:
            raise ValueError("No keywords provided")

        stmt = select(Keyword.name).where(Keyword.name.in_(unique_keywords))
        result = await self.db.execute(stmt)
        existing_names = {row[0] for row in result.fetchall()}

        new_keywords = [
            kw for kw in unique_keywords.values() if kw.name not in existing_names
        ]

        if not new_keywords:
            raise ValueError("All keywords already exist")

        async with transaction(self.db):
            values = [keyword.model_dump() for keyword in new_keywords]
            await self.db.execute(insert(Keyword).values(values))

    async def get_keyword(self, keyword_id: int):
        """获取单个关键词"""
        result = await self.db.execute(select(Keyword).where(Keyword.id == keyword_id))
        return result.scalar_one_or_none()

    async def get_keyword_by_name(self, name: str):
        """通过名称获取关键词"""
        result = await self.db.execute(select(Keyword).where(Keyword.name == name))
        return result.scalar_one_or_none()

    async def get_keywords(self):
        """获取所有关键词"""
        result = await self.db.execute(select(Keyword))
        return result.scalars().all()

    async def get_keyword_list(
        self, skip: int = 0, limit: int = 10, subject: list[Subject] | None = None
    ):
        """获取所有关键词"""
        query = select(Keyword)
        count_query = select(func.count(Keyword.id))

        if subject:
            query = query.where(Keyword.subject.in_(subject))
            count_query = count_query.where(Keyword.subject.in_(subject))

        # 获取总数
        result = await self.db.execute(count_query)
        total = result.scalar_one()

        # 获取分页数据
        result = await self.db.execute(query.offset(skip).limit(limit))
        kws = result.scalars().all()
        items = [KeywordItem.model_validate(kw) for kw in kws]

        return items, total

    async def delete_keyword(self, keyword_id: int) -> bool:
        """删除关键词"""
        db_keyword = await self.get_keyword(keyword_id)
        if db_keyword is None:
            return False

        async with transaction(self.db):
            await self.db.delete(db_keyword)
        return True
