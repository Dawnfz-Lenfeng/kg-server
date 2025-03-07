import pytest
from kgtools.schemas.preprocessing import ExtractConfig, NormalizeConfig, OCREngine

from app.schemas.document import DocCreate, DocState, DocUpdate
from app.services import DocService


@pytest.mark.asyncio
async def test_create_doc(
    uploaded_file_name: str,
    doc_svc: DocService,
):
    """测试创建文档"""
    doc_create = DocCreate(
        title="新建文档",
        local_file_name=uploaded_file_name,
        file_type="pdf",
    )
    doc = await doc_svc.create_doc(doc_create)

    assert doc.id is not None
    assert doc.title == "新建文档"
    assert doc.file_type == "pdf"
    assert doc.state == DocState.UPLOADED

    await doc_svc.delete_doc(doc_id=doc.id)


@pytest.mark.asyncio
async def test_read_doc(sample_doc: int, doc_svc: DocService):
    """测试读取单个文档"""
    doc = await doc_svc.read_doc(doc_id=sample_doc)

    assert doc is not None
    assert doc.id == sample_doc
    assert doc.title


@pytest.mark.asyncio
async def test_update_doc(
    sample_doc: int,
    doc_svc: DocService,
):
    """测试修改文档"""
    new_title = "更新后的标题"

    updated = await doc_svc.update_doc(
        doc_id=sample_doc,
        doc_update=DocUpdate(title=new_title),
    )

    assert updated is not None
    assert updated.title == new_title


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
    config = ExtractConfig(ocr_engine=ocr_engine, force_ocr=True, last_page=1)
    doc = await doc_svc.extract_doc(
        doc_id=sample_doc,
        extract_config=config,
    )

    assert doc is not None
    assert doc.state == DocState.EXTRACTED


@pytest.mark.asyncio
async def test_normalize_doc_text(sample_doc: int, doc_svc: DocService):
    """测试清洗文档文本"""
    await doc_svc.extract_doc(
        doc_id=sample_doc, extract_config=ExtractConfig(last_page=1)
    )

    doc = await doc_svc.normalize_doc(
        doc_id=sample_doc, normalize_config=NormalizeConfig()
    )

    assert doc is not None
    assert doc.state == DocState.NORMALIZED
