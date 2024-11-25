from pathlib import Path

import pytest
import pytest_asyncio
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.schemas.preprocessing import ExtractConfig, NormalizeConfig, OCREngine
from app.services.document import (
    create_doc_service,
    delete_doc_service,
    extract_doc_text_service,
    normalize_doc_text_service,
    read_doc_service,
    read_docs_service,
    update_doc_service,
)

SAMPLES_DIR = Path(__file__).parent.parent / "samples"


@pytest.fixture
def pdf_file():
    """提供测试用PDF文件"""
    pdf_path = SAMPLES_DIR / "sample.pdf"
    with open(pdf_path, "rb") as f:
        yield UploadFile(file=f, filename="sample.pdf")


@pytest_asyncio.fixture
async def sample_doc(db: Session, pdf_file: UploadFile):
    """创建测试文档"""
    doc = await create_doc_service(
        doc=DocumentCreate(title="测试文档", file_type="pdf", subject_id=1),
        file=pdf_file,
        db=db,
    )
    yield doc
    await delete_doc_service(doc_id=doc.id, db=db)


@pytest.mark.asyncio
async def test_create_doc(db: Session, pdf_file: UploadFile):
    """测试创建文档"""
    doc = await create_doc_service(
        doc=DocumentCreate(title="新建文档", file_type="pdf", subject_id=1),
        file=pdf_file,
        db=db,
    )

    assert doc.id is not None
    assert doc.title == "新建文档"
    assert doc.file_type == "pdf"


@pytest.mark.asyncio
async def test_read_doc(db: Session, sample_doc: Document):
    """测试读取单个文档"""
    doc = await read_doc_service(doc_id=sample_doc.id, db=db)

    assert doc is not None
    assert doc.id == sample_doc.id
    assert doc.title == sample_doc.title


@pytest.mark.asyncio
async def test_update_doc(db: Session, sample_doc: Document):
    """测试修改文档"""
    new_title = "更新后的标题"
    updated = await update_doc_service(
        doc_id=sample_doc.id,
        doc_update=DocumentUpdate(title=new_title),
        db=db,
    )

    assert updated is not None
    assert updated.title == new_title
    assert updated.id == sample_doc.id


@pytest.mark.asyncio
async def test_delete_doc(db: Session, sample_doc: Document):
    """测试删除文档"""
    result = await delete_doc_service(doc_id=sample_doc.id, db=db)
    assert result is True

    # 验证确实被删除了
    doc = await read_doc_service(doc_id=sample_doc.id, db=db)
    assert doc is None


@pytest.mark.asyncio
@pytest.mark.parametrize("ocr_engine", list(OCREngine))
async def test_extract_doc_text(
    db: Session, sample_doc: Document, ocr_engine: OCREngine
):
    """测试提取文档文本"""
    config = ExtractConfig(num_workers=2, ocr_engine=ocr_engine)
    doc = await extract_doc_text_service(
        doc_id=sample_doc.id,
        extract_config=config,
        db=db,
    )

    assert doc is not None
    assert doc.origin_text is not None


@pytest.mark.asyncio
async def test_normalize_doc_text(db: Session, sample_doc: Document):
    """测试清洗文档文本"""
    # 先提取文本
    await extract_doc_text_service(
        doc_id=sample_doc.id,
        extract_config=ExtractConfig(),
        db=db,
    )

    # 再清洗文本
    config = NormalizeConfig(char_threshold=2)
    doc = await normalize_doc_text_service(
        doc_id=sample_doc.id,
        normalize_config=config,
        db=db,
    )

    assert doc is not None
    assert doc.processed_text is not None
