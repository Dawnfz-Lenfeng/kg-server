import pytest

from app.models import Document, Keyword
from app.schemas.base import SetOperation
from app.schemas.document import DocCreate, DocUpdate
from app.schemas.preprocessing import ExtractConfig, NormalizeConfig, OCREngine
from app.services import DocService


def test_create_doc(
    sample_keywords: list[Keyword],
    uploaded_file_name: str,
    doc_svc: DocService,
):
    """测试创建文档"""
    doc_create = DocCreate(
        title="新建文档",
        file_name=uploaded_file_name,
        file_type="pdf",
        subject_id=1,
        keyword_ids=[sample_keywords[0].id, sample_keywords[1].id],
    )
    doc = doc_svc.create_doc(doc=doc_create)

    assert doc.id is not None
    assert doc.title == "新建文档"
    assert doc.file_type == "pdf"

    keyword_ids = {kw.id for kw in doc.keywords}
    assert len(keyword_ids) == 2
    assert sample_keywords[0].id in keyword_ids
    assert sample_keywords[1].id in keyword_ids

    doc_svc.delete_doc(doc_id=doc.id)


def test_read_doc(sample_doc: Document, doc_svc: DocService):
    """测试读取单个文档"""
    doc = doc_svc.read_doc(doc_id=sample_doc.id)

    assert doc is not None
    assert doc.id == sample_doc.id
    assert doc.title == sample_doc.title

    assert len(doc.keywords) == 2


def test_update_doc(
    sample_doc: Document,
    sample_keywords: list[Keyword],
    doc_svc: DocService,
):
    """测试修改文档"""
    new_title = "更新后的标题"
    keywords_update = SetOperation(
        add=[sample_keywords[2].id],  # 添加第三个关键词
        remove=[sample_keywords[0].id],  # 移除第一个关键词
    )

    updated = doc_svc.update_doc(
        doc_id=sample_doc.id,
        doc_update=DocUpdate(title=new_title, keywords=keywords_update),
    )

    assert updated is not None
    assert updated.title == new_title
    assert updated.id == sample_doc.id

    keyword_ids = {kw.id for kw in updated.keywords}
    assert len(keyword_ids) == 2
    assert sample_keywords[2].id in keyword_ids  # 新添加的关键词
    assert sample_keywords[1].id in keyword_ids  # 未变动的关键词
    assert sample_keywords[0].id not in keyword_ids  # 已移除的关键词


def test_delete_doc(sample_doc: Document, doc_svc: DocService):
    """测试删除文档"""
    result = doc_svc.delete_doc(doc_id=sample_doc.id)
    assert result is True

    doc = doc_svc.read_doc(doc_id=sample_doc.id)
    assert doc is None


@pytest.mark.parametrize("ocr_engine", list(OCREngine))
def test_extract_doc_text(
    sample_doc: Document, ocr_engine: OCREngine, doc_svc: DocService
):
    """测试提取文档文本"""
    config = ExtractConfig(ocr_engine=ocr_engine, force_ocr=True)
    doc = doc_svc.extract_doc_text(
        doc_id=sample_doc.id,
        extract_config=config,
    )

    assert doc is not None
    assert doc.is_extracted


def test_normalize_doc_text(sample_doc: Document, doc_svc: DocService):
    """测试清洗文档文本"""
    doc_svc.extract_doc_text(doc_id=sample_doc.id, extract_config=ExtractConfig())

    doc = doc_svc.normalize_doc_text(
        doc_id=sample_doc.id, normalize_config=NormalizeConfig()
    )

    assert doc is not None
    assert doc.is_normalized
