from typing import List, Optional

from sqlalchemy.orm import Session

from ..models.document import Document
from ..models.keyword import Keyword, document_keywords


async def create_keyword(db: Session, name: str) -> Keyword:
    """创建关键词"""
    db_keyword = Keyword(name=name)
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword


async def get_keyword(
    db: Session, keyword_id: Optional[int] = None, keyword_name: Optional[str] = None
) -> Optional[Keyword]:
    """获取单个关键词（通过ID或名称）"""
    if not (keyword_id or keyword_name):
        return None

    query = db.query(Keyword)
    if keyword_id:
        query = query.filter(Keyword.id == keyword_id)
    if keyword_name:
        query = query.filter(Keyword.name == keyword_name)

    return query.first()


async def get_keywords(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search_name: Optional[str] = None,
) -> List[Keyword]:
    """获取关键词列表，支持搜索名称"""
    query = db.query(Keyword)

    if search_name:
        query = query.filter(
            Keyword.name.ilike(f"%{search_name}%"),
        )

    return query.offset(skip).limit(limit).all()


async def delete_keyword(db: Session, keyword_id: int) -> bool:
    """删除关键词"""
    keyword = await get_keyword(db, keyword_id)
    if keyword:
        db.delete(keyword)
        db.commit()
        return True
    return False


async def create_document_keyword(
    db: Session, document_id: int, keyword_id: int
) -> Optional[dict]:
    """为文档添加关键词"""
    document = db.query(Document).filter(Document.id == document_id).first()
    keyword = await get_keyword(db, keyword_id)

    if not (document and keyword):
        return None

    # 添加关联关系
    stmt = document_keywords.insert().values(
        document_id=document_id,
        keyword_id=keyword_id,
    )
    db.execute(stmt)
    db.commit()

    # 构造响应
    return {
        "document_id": document_id,
        "keyword": keyword,
    }


async def get_document_keywords(db: Session, document_id: int) -> List[dict]:
    """获取文档的关键词列表"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        return []

    # 获取关联数据
    results = (
        db.query(document_keywords, Keyword)
        .join(Keyword, document_keywords.c.keyword_id == Keyword.id)
        .filter(document_keywords.c.document_id == document_id)
        .all()
    )

    return [
        {
            "document_id": document_id,
            "keyword": result.Keyword,
        }
        for result in results
    ]


async def delete_document_keyword(
    db: Session, document_id: int, keyword_id: int
) -> bool:
    """删除文档的关键词关联"""
    stmt = document_keywords.delete().where(
        document_keywords.c.document_id == document_id,
        document_keywords.c.keyword_id == keyword_id,
    )
    result = db.execute(stmt)
    db.commit()
    return result.rowcount > 0
