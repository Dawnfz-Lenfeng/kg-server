from pathlib import Path

import pytest
import pytest_asyncio
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.services.document import (
    create_document,
    delete_document,
    get_document,
    get_documents,
    update_document,
)

SAMPLES_DIR = Path(__file__).parent.parent / "samples"


@pytest.fixture
def pdf_file():
    """提供测试用PDF文件"""
    pdf_path = SAMPLES_DIR / "sample.pdf"
    with open(pdf_path, "rb") as f:
        yield UploadFile(file=f, filename="sample.pdf")


@pytest_asyncio.fixture
async def sample_document(db: Session, pdf_file: UploadFile):
    """创建一个测试文档"""
    doc = await create_document(
        db=db,
        document=DocumentCreate(title="测试文档", file_type="pdf", subject_id=1),
        file=pdf_file,
    )
    yield doc
    await delete_document(db, doc.id)


@pytest.mark.asyncio
async def test_create_document(db: Session, pdf_file: UploadFile):
    """测试创建文档"""
    doc = await create_document(
        db=db,
        document=DocumentCreate(title="新建文档", file_type="pdf", subject_id=1),
        file=pdf_file,
    )

    assert doc.id is not None
    assert doc.title == "新建文档"
    assert doc.file_type == "pdf"
    assert doc.origin_text
    assert doc.processed_text


@pytest.mark.asyncio
async def test_get_document(db: Session, sample_document: Document):
    """测试获取单个文档"""
    doc = await get_document(db, sample_document.id)

    assert doc is not None
    assert doc.id == sample_document.id
    assert doc.title == sample_document.title


@pytest.mark.asyncio
async def test_get_documents(db: Session, sample_document: Document):
    """测试获取文档列表"""
    docs = await get_documents(db, skip=0, limit=10)

    assert len(docs) > 0
    assert any(d.id == sample_document.id for d in docs)


@pytest.mark.asyncio
async def test_update_document(db: Session, sample_document: Document):
    """测试更新文档"""
    new_title = "更新后的标题"
    updated = await update_document(
        db,
        sample_document.id,
        DocumentUpdate(title=new_title),
    )

    assert updated is not None
    assert updated.title == new_title
    assert updated.id == sample_document.id


@pytest.mark.asyncio
async def test_delete_document(db: Session, sample_document: Document):
    """测试删除文档"""
    result = await delete_document(db, sample_document.id)
    assert result is True

    # 验证确实被删除了
    doc = await get_document(db, sample_document.id)
    assert doc is None


@pytest.mark.asyncio
@pytest.mark.parametrize("ocr_engine", ["cnocr", "tesseract", "paddleocr"])
async def test_create_with_different_engines(
    db: Session, pdf_file: UploadFile, ocr_engine: str
):
    """测试不同OCR引擎的文档创建"""
    try:
        doc = await create_document(
            db=db,
            document=DocumentCreate(
                title=f"{ocr_engine} test", file_type="pdf", subject_id=1
            ),
            file=pdf_file,
            ocr_engine=ocr_engine,
            force_ocr=True,
        )
        assert doc.origin_text
        assert doc.processed_text
    except ImportError:
        pytest.skip(f"{ocr_engine} not installed")
