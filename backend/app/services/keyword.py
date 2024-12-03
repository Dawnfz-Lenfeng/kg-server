from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import transaction
from ..models.document import Document
from ..models.keyword import Keyword
from ..schemas.keyword import KeywordCreate, KeywordUpdate


class KeywordService:
    def __init__(self, db: Session):
        self.db = db

    def read_keyword_service(self, keyword_id: int) -> Keyword | None:
        """获取单个关键词"""
        stmt = select(Keyword).where(Keyword.id == keyword_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def read_keyword_by_name_service(self, name: str) -> Keyword | None:
        """通过名称获取关键词"""
        stmt = select(Keyword).where(Keyword.name == name)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def create_keyword_service(self, keyword: KeywordCreate) -> Keyword:
        """创建关键词"""
        existing = self.read_keyword_by_name_service(keyword.name)
        if existing:
            raise HTTPException(
                status_code=400, detail=f"关键词 '{keyword.name}' 已存在"
            )

        try:
            with transaction(self.db):
                db_keyword = Keyword(name=keyword.name)
                if keyword.document_ids:
                    stmt = select(Document).where(Document.id.in_(keyword.document_ids))
                    documents = set(self.db.execute(stmt).scalars().all())
                    db_keyword.documents = documents

                self.db.add(db_keyword)

            self.db.refresh(db_keyword)
            return db_keyword
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"创建关键词失败: {str(e)}"
            ) from e

    def read_keywords_service(
        self, skip: int, limit: int, search: str | None
    ) -> Sequence[Keyword]:
        """获取关键词列表"""
        stmt = select(Keyword)
        if search:
            stmt = stmt.where(Keyword.name.ilike(f"%{search}%"))
        stmt = stmt.offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return result.scalars().all()

    async def update_keyword_service(
        self, keyword_id: int, keyword_update: KeywordUpdate
    ) -> Keyword | None:
        """更新关键词"""
        db_keyword = self.read_keyword_service(keyword_id)
        if db_keyword is None:
            return None

        try:
            with transaction(self.db):
                if keyword_update.name and keyword_update.name != db_keyword.name:
                    existing = self.read_keyword_by_name_service(keyword_update.name)
                    if existing:
                        raise HTTPException(
                            status_code=400,
                            detail=f"关键词 '{keyword_update.name}' 已存在",
                        )
                    db_keyword.name = keyword_update.name

                if keyword_update.documents is not None:
                    if keyword_update.documents.add:
                        stmt = select(Document).where(
                            Document.id.in_(keyword_update.documents.add)
                        )
                        docs_to_add = set(self.db.execute(stmt).scalars().all())
                        db_keyword.documents |= docs_to_add

                    if keyword_update.documents.remove:
                        stmt = select(Document).where(
                            Document.id.in_(keyword_update.documents.remove)
                        )
                        docs_to_remove = set(self.db.execute(stmt).scalars().all())
                        db_keyword.documents -= docs_to_remove

                self.db.add(db_keyword)

            self.db.refresh(db_keyword)
            return db_keyword
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"更新关键词失败: {str(e)}"
            ) from e

    async def delete_keyword_service(self, keyword_id: int) -> bool:
        """删除关键词"""
        db_keyword = self.read_keyword_service(keyword_id)
        if db_keyword is not None:
            try:
                with transaction(self.db):
                    self.db.delete(db_keyword)
                return True
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"删除关键词失败: {str(e)}"
                ) from e

        return False
