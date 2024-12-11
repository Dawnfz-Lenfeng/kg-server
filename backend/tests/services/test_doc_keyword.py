import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import DocKeywordService


@pytest.fixture
def doc_kw_svc(db: AsyncSession):
    return DocKeywordService(db)


async def test_create_keywords_for_doc(doc_kw_svc: DocKeywordService, sample_doc: int):
    """测试为文档创建关键词"""
    keywords = ["关键词1", "关键词2", "关键词3"]

    doc = await doc_kw_svc.create_keywards_for_doc(sample_doc, keywords)

    assert doc is not None
    assert len(doc.keywords) == 3
    assert all(k.name in keywords for k in doc.keywords)

    for keyword in keywords:
        await doc_kw_svc.kw_svc.delete_keyword_by_name(keyword)


async def test_create_keywords_for_nonexistent_doc(doc_kw_svc: DocKeywordService):
    """测试为不存在的文档创建关键词"""
    doc = await doc_kw_svc.create_keywards_for_doc(999, ["测试"])
    assert doc is None
