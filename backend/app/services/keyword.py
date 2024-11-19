from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.document import Document
from ..models.keyword import Keyword


async def create_keyword(db: Session, name: str) -> Keyword:
    """创建关键词"""
    db_keyword = Keyword(name=name)
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword


async def get_keyword(
    db: Session, keyword_id: int | None = None, keyword_name: str | None = None
) -> Keyword | None:
    """获取单个关键词（通过ID或名称）"""
    if not (keyword_id or keyword_name):
        return None

    stmt = select(Keyword)
    if keyword_id:
        stmt = stmt.where(Keyword.id == keyword_id)
    if keyword_name:
        stmt = stmt.where(Keyword.name == keyword_name)

    result = db.execute(stmt)
    return result.scalar_one_or_none()


async def get_keywords(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search_name: str | None = None,
) -> Sequence[Keyword]:
    """获取关键词列表，支持搜索名称"""
    stmt = select(Keyword)

    if search_name:
        stmt = stmt.where(Keyword.name.ilike(f"%{search_name}%"))

    stmt = stmt.offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


async def delete_keyword(db: Session, keyword_id: int) -> bool:
    """删除关键词"""
    keyword = await get_keyword(db, keyword_id)
    if keyword is not None:
        db.delete(keyword)
        db.commit()
        return True
    return False


async def create_document_keyword(
    db: Session, document_id: int, keyword_id: int
) -> dict | None:
    """为文档添加关键词"""
    stmt = select(Document).where(Document.id == document_id)
    document = db.execute(stmt).scalar_one_or_none()

    keyword = await get_keyword(db, keyword_id)

    if not (document and keyword):
        return None

    document.keywords.append(keyword)
    db.commit()

    return {
        "document_id": document_id,
        "keyword": keyword,
    }


async def get_document_keywords(db: Session, document_id: int) -> Sequence[dict]:
    """获取文档的关键词列表"""
    stmt = select(Document).where(Document.id == document_id)
    document = db.execute(stmt).scalar_one_or_none()
    if not document:
        return []

    return [
        {
            "document_id": document_id,
            "keyword": keyword.name,
        }
        for keyword in document.keywords
    ]


async def delete_document_keyword(
    db: Session, document_id: int, keyword_id: int
) -> bool:
    """删除文档的关键词关联"""
    stmt = select(Document).where(Document.id == document_id)
    document = db.execute(stmt).scalar_one_or_none()
    if not document:
        return False

    keyword = await get_keyword(db, keyword_id)
    if not keyword:
        return False

    # 删除关联关系
    document.keywords.remove(keyword)
    db.commit()

    return True
