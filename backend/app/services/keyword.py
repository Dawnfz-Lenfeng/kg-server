from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import transaction
from ..models.document import Document
from ..models.keyword import Keyword
from ..schemas.keyword import KeywordCreate, KeywordUpdate


async def create_keyword_service(
    keyword: KeywordCreate,
    db: Session,
) -> Keyword:
    """创建关键词"""
    existing = read_keyword_by_name_service(keyword.name, db)
    if existing:
        raise HTTPException(status_code=400, detail=f"关键词 '{keyword.name}' 已存在")

    with transaction(db):
        db_keyword = Keyword(name=keyword.name)
        if keyword.document_ids:
            stmt = select(Document).where(Document.id.in_(keyword.document_ids))
            documents = set(db.execute(stmt).scalars().all())
            db_keyword.documents = documents

        db.add(db_keyword)

    db.refresh(db_keyword)
    return db_keyword


def read_keyword_service(
    keyword_id: int,
    db: Session,
) -> Keyword | None:
    """获取单个关键词"""
    stmt = select(Keyword).where(Keyword.id == keyword_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def read_keyword_by_name_service(
    name: str,
    db: Session,
) -> Keyword | None:
    """通过名称获取关键词"""
    stmt = select(Keyword).where(Keyword.name == name)
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def read_keywords_service(
    skip: int,
    limit: int,
    search: str | None,
    db: Session,
) -> Sequence[Keyword]:
    """获取关键词列表"""
    stmt = select(Keyword)
    if search:
        stmt = stmt.where(Keyword.name.ilike(f"%{search}%"))
    stmt = stmt.offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


async def update_keyword_service(
    keyword_id: int,
    keyword_update: KeywordUpdate,
    db: Session,
) -> Keyword | None:
    """更新关键词"""
    db_keyword = read_keyword_service(keyword_id, db)
    if db_keyword is None:
        return None

    with transaction(db):
        if keyword_update.name and keyword_update.name != db_keyword.name:
            existing = read_keyword_by_name_service(keyword_update.name, db)
            if existing:
                raise HTTPException(
                    status_code=400, detail=f"关键词 '{keyword_update.name}' 已存在"
                )
            db_keyword.name = keyword_update.name

        if keyword_update.documents is not None:
            if keyword_update.documents.add:
                stmt = select(Document).where(
                    Document.id.in_(keyword_update.documents.add)
                )
                docs_to_add = set(db.execute(stmt).scalars().all())
                db_keyword.documents |= docs_to_add

            if keyword_update.documents.remove:
                stmt = select(Document).where(
                    Document.id.in_(keyword_update.documents.remove)
                )
                docs_to_remove = set(db.execute(stmt).scalars().all())
                db_keyword.documents -= docs_to_remove

        db.add(db_keyword)

    db.refresh(db_keyword)
    return db_keyword


async def delete_keyword_service(
    keyword_id: int,
    db: Session,
) -> bool:
    """删除关键词"""
    db_keyword = read_keyword_service(keyword_id, db)
    if db_keyword is not None:
        with transaction(db):
            db.delete(db_keyword)
        return True

    return False
