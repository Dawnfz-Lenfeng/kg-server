import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.keyword import KeywordAlreadyExistsError
from app.schemas.keyword import KeywordCreate
from app.services import KeywordService


@pytest.fixture
def kw_svc(db: AsyncSession):
    return KeywordService(db)


async def test_create_keyword(kw_svc: KeywordService):
    """测试创建关键词"""
    keyword = await kw_svc.create_keyword(KeywordCreate(name="测试关键词"))

    assert keyword.name == "测试关键词"
    await kw_svc.delete_keyword(keyword.id)


async def test_create_duplicate_keyword(kw_svc: KeywordService):
    """测试创建重复关键词"""
    keyword = await kw_svc.create_keyword(KeywordCreate(name="重复关键词"))

    with pytest.raises(KeywordAlreadyExistsError):
        await kw_svc.create_keyword(KeywordCreate(name="重复关键词"))

    await kw_svc.delete_keyword(keyword.id)


async def test_read_keyword(kw_svc: KeywordService):
    """测试读取关键词"""
    created = await kw_svc.create_keyword(KeywordCreate(name="测试关键词"))
    keyword = await kw_svc.read_keyword(created.id)

    assert keyword is not None
    assert keyword.name == "测试关键词"

    await kw_svc.delete_keyword(keyword.id)


async def test_read_keywords(kw_svc: KeywordService):
    """测试读取关键词列表"""
    # 创建测试数据
    names = ["关键词1", "关键词2", "测试3"]
    for name in names:
        await kw_svc.create_keyword(KeywordCreate(name=name))

    # 测试基本查询
    keywords = await kw_svc.read_keywords(skip=0, limit=10)
    assert len(keywords) == 3

    # 测试搜索
    keywords = await kw_svc.read_keywords(skip=0, limit=10, search="关键词")
    assert len(keywords) == 2

    for name in names:
        await kw_svc.delete_keyword_by_name(name)
