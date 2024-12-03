import pytest

from app.schemas.base import SetOperation
from app.schemas.document import DocCreate, DocUpdate
from app.schemas.preprocessing import ExtractConfig, NormalizeConfig, OCREngine
from app.services import DocService


@pytest.mark.asyncio
async def test_create_doc(
    sample_keywords: list[int],
    uploaded_file_name: str,
    doc_svc: DocService,
):
    """测试创建文档"""
    doc_create = DocCreate(
        title="新建文档",
        file_name=uploaded_file_name,
        file_type="pdf",
        subject_id=1,
        keyword_ids=sample_keywords[0:2],
    )
    doc = await doc_svc.create_doc(doc_create)

    assert doc.id is not None
    assert doc.title == "新建文档"
    assert doc.file_type == "pdf"

    keyword_ids = {kw.id for kw in doc.keywords}
    assert len(keyword_ids) == 2
    assert sample_keywords[0] in keyword_ids
    assert sample_keywords[1] in keyword_ids

    await doc_svc.delete_doc(doc_id=doc.id)


@pytest.mark.asyncio
async def test_read_doc(sample_doc: int, doc_svc: DocService):
    """测试读取单个文档"""
    doc = await doc_svc.read_doc(doc_id=sample_doc)

    assert doc is not None
    assert doc.id == sample_doc
    assert doc.title

    assert len(doc.keywords) == 2


@pytest.mark.asyncio
async def test_update_doc(
    sample_doc: int,
    sample_keywords: list[int],
    doc_svc: DocService,
):
    """测试修改文档"""
    new_title = "更新后的标题"
    keywords_update = SetOperation(
        add=[sample_keywords[2]],  # 添加第三个关键词
        remove=[sample_keywords[0]],  # 移除第一个关键词
    )

    updated = await doc_svc.update_doc(
        doc_id=sample_doc,
        doc_update=DocUpdate(title=new_title, keywords=keywords_update),
    )

    assert updated is not None
    assert updated.title == new_title
    assert updated.id == sample_doc

    keyword_ids = {kw.id for kw in updated.keywords}
    assert len(keyword_ids) == 2
    assert sample_keywords[2] in keyword_ids  # 新添加的关键词
    assert sample_keywords[1] in keyword_ids  # 未变动的关键词
    assert sample_keywords[0] not in keyword_ids  # 已移除的关键词


@pytest.mark.asyncio
async def test_delete_doc(sample_doc: int, doc_svc: DocService):
    """测试删除文档"""
    result = await doc_svc.delete_doc(doc_id=sample_doc)
    assert result is True

    doc = await doc_svc.read_doc(doc_id=sample_doc)
    assert doc is None


@pytest.mark.asyncio
@pytest.mark.parametrize("ocr_engine", list(OCREngine))
async def test_extract_doc_text(
    sample_doc: int, ocr_engine: OCREngine, doc_svc: DocService
):
    """测试提取文档文本"""
    config = ExtractConfig(ocr_engine=ocr_engine, force_ocr=True)
    doc = await doc_svc.extract_doc_text(
        doc_id=sample_doc,
        extract_config=config,
    )

    assert doc is not None
    assert doc.is_extracted


@pytest.mark.asyncio
async def test_normalize_doc_text(sample_doc: int, doc_svc: DocService):
    """测试清洗文档文本"""
    await doc_svc.extract_doc_text(doc_id=sample_doc, extract_config=ExtractConfig())

    doc = await doc_svc.normalize_doc_text(
        doc_id=sample_doc, normalize_config=NormalizeConfig()
    )

    assert doc is not None
    assert doc.is_normalized
