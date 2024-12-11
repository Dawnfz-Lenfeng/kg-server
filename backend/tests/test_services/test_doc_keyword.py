import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Document, Keyword
from app.schemas.document import DocCreate, FileType
from app.schemas.keyword import KeywordCreate
from app.services import DocKeywordService, DocService


@pytest.fixture
def doc_kw_svc(db_session: AsyncSession):
    return DocKeywordService(db_session)


@pytest.fixture
async def test_doc(db_session: AsyncSession) -> Document:
    """创建测试文档"""
    doc_svc = DocService(db_session)
    return await doc_svc.create_doc(
        DocCreate(
            title="测试文档",
            file_name="test",
            file_type=FileType.PDF,
            subject_id=1,
        )
    )


async def test_create_keywords_for_doc(
    doc_kw_svc: DocKeywordService, test_doc: Document
):
    """测试为文档创建关键词"""
    keywords = ["关键词1", "关键词2", "关键词3"]
    
    doc = await doc_kw_svc.create_keywards_for_doc(test_doc.id, keywords)
    
    assert doc is not None
    assert len(doc.keywords) == 3
    assert all(k.name in keywords for k in doc.keywords)


async def test_create_keywords_for_nonexistent_doc(doc_kw_svc: DocKeywordService):
    """测试为不存在的文档创建关键词"""
    doc = await doc_kw_svc.create_keywards_for_doc(999, ["测试"])
    assert doc is None 