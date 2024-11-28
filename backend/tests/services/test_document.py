import pytest
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.keyword import Keyword
from app.schemas.base import SetOperation
from app.schemas.document import DocCreate, DocUpdate
from app.schemas.preprocessing import ExtractConfig, NormalizeConfig, OCREngine
from app.services.document import (
    create_doc_service,
    create_docs_service,
    delete_doc_service,
    extract_doc_text_service,
    normalize_doc_text_service,
    read_doc_service,
    save_uploaded_file,
    update_doc_service,
)


@pytest.mark.asyncio
async def test_create_doc(
    db: Session, pdf_file: UploadFile, sample_keywords: list[Keyword]
):
    """测试创建文档"""
    doc_create = DocCreate(
        title="新建文档",
        file_path=await save_uploaded_file(file=pdf_file),
        file_type="pdf",
        subject_id=1,
        keyword_ids=[sample_keywords[0].id, sample_keywords[1].id],
    )
    result = await create_doc_service(doc=doc_create, db=db)

    assert result.success
    assert result.error is None
    assert result.document is not None

    doc = result.document
    assert doc.id is not None
    assert doc.title == "新建文档"
    assert doc.file_type == "pdf"

    keyword_ids = {kw.id for kw in doc.keywords}
    assert len(keyword_ids) == 2
    assert sample_keywords[0].id in keyword_ids
    assert sample_keywords[1].id in keyword_ids

    await delete_doc_service(doc_id=doc.id, db=db)


@pytest.mark.asyncio
async def test_batch_create_docs(
    db: Session, pdf_file: UploadFile, sample_keywords: list[Keyword]
):
    """测试批量创建文档"""
    docs = [
        DocCreate(
            title=f"文档{i}",
            file_path=await save_uploaded_file(file=pdf_file),
            file_type="pdf",
            subject_id=1,
            keyword_ids=[k.id for k in sample_keywords[:2]],
        )
        for i in range(3)
    ]

    results = await create_docs_service(docs=docs, db=db)

    assert len(results) == 3
    assert all(r.success for r in results)
    assert all(r.document is not None for r in results)
    assert all(r.error is None for r in results)

    for result in results:
        if result.document:
            await delete_doc_service(doc_id=result.document.id, db=db)


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
    await extract_doc_text_service(
        doc_id=sample_doc.id,
        extract_config=ExtractConfig(),
        db=db,
    )

    config = NormalizeConfig(char_threshold=2)
    doc = await normalize_doc_text_service(
        doc_id=sample_doc.id,
        normalize_config=config,
        db=db,
    )

    assert doc is not None
    assert doc.processed_text is not None
