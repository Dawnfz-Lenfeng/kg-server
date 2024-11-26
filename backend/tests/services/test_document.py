from pathlib import Path

import pytest
import pytest_asyncio
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.keyword import Keyword
from app.schemas.base import SetOperation
from app.schemas.document import DocCreate, DocUpdate
from app.schemas.preprocessing import ExtractConfig, NormalizeConfig, OCREngine
from app.services.document import (
    create_doc_service,
    delete_doc_service,
    extract_doc_text_service,
    normalize_doc_text_service,
    read_doc_service,
    update_doc_service,
)

SAMPLES_DIR = Path(__file__).parent.parent / "samples"


@pytest.fixture
def sample_keywords(db: Session):
    """创建测试用关键词"""
    keywords = [
        Keyword(name="测试关键词1"),
        Keyword(name="测试关键词2"),
        Keyword(name="测试关键词3"),
    ]
    for kw in keywords:
        db.add(kw)
    db.commit()
    for kw in keywords:
        db.refresh(kw)
    yield keywords
    for kw in keywords:
        db.delete(kw)
    db.commit()


@pytest.fixture
def pdf_file():
    """提供测试用PDF文件"""
    pdf_path = SAMPLES_DIR / "sample.pdf"
    with pdf_path.open("rb") as f:
        yield UploadFile(file=f, filename="sample.pdf")


@pytest_asyncio.fixture
async def sample_doc(db: Session, pdf_file: UploadFile, sample_keywords: list[Keyword]):
    """创建测试文档"""
    doc = DocCreate(
        title="测试文档",
        file="pdf",
        subject_id=1,
        keyword_ids=[k.id for k in sample_keywords[:2]],  # 关联前两个关键词
    )
    db_doc = await create_doc_service(file=pdf_file, doc=doc, db=db)
    yield db_doc
    await delete_doc_service(doc_id=db_doc.id, db=db)


@pytest.mark.asyncio
async def test_create_doc(
    db: Session, pdf_file: UploadFile, sample_keywords: list[Keyword]
):
    """测试创建文档"""
    doc_create = DocCreate(
        title="新建文档",
        subject_id=1,
        keyword_ids=[sample_keywords[0].id, sample_keywords[1].id],
    )
    doc = await create_doc_service(file=pdf_file, doc=doc_create, db=db)

    assert doc.id is not None
    assert doc.title == "新建文档"
    assert doc.file_type == "pdf"

    keyword_ids = {kw.id for kw in doc.keywords}
    assert len(keyword_ids) == 2
    assert sample_keywords[0].id in keyword_ids
    assert sample_keywords[1].id in keyword_ids


@pytest.mark.asyncio
async def test_read_doc(db: Session, sample_doc: Document):
    """测试读取单个文档"""
    doc = await read_doc_service(doc_id=sample_doc.id, db=db)

    assert doc is not None
    assert doc.id == sample_doc.id
    assert doc.title == sample_doc.title

    assert len(doc.keywords) == 2


@pytest.mark.asyncio
async def test_update_doc(
    db: Session, sample_doc: Document, sample_keywords: list[Keyword]
):
    """测试修改文档"""
    new_title = "更新后的标题"
    keywords_update = SetOperation(
        add=[sample_keywords[2].id],  # 添加第三个关键词
        remove=[sample_keywords[0].id],  # 移除第一个关键词
    )

    updated = await update_doc_service(
        doc_id=sample_doc.id,
        doc_update=DocUpdate(title=new_title, keywords=keywords_update),
        db=db,
    )

    assert updated is not None
    assert updated.title == new_title
    assert updated.id == sample_doc.id

    keyword_ids = {kw.id for kw in updated.keywords}
    assert len(keyword_ids) == 2
    assert sample_keywords[2].id in keyword_ids  # 新添加的关键词
    assert sample_keywords[1].id in keyword_ids  # 未变动的关键词
    assert sample_keywords[0].id not in keyword_ids  # 已移除的关键词


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
    config = ExtractConfig(ocr_engine=ocr_engine, force_ocr=True)
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
