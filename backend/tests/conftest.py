from pathlib import Path

import pytest
import pytest_asyncio
from fastapi import UploadFile
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, transaction
from app.models.keyword import Keyword
from app.schemas.document import DocCreate
from app.services.document import (
    create_doc_service,
    delete_doc_service,
    save_uploaded_file,
)

SAMPLES_DIR = Path(__file__).parent / "samples"


@pytest.fixture(scope="session")
def engine():
    """创建内存数据库引擎"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db(engine: Engine):
    """提供数据库会话"""
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def sample_keywords(db: Session):
    """创建测试用关键词"""
    keywords = [
        Keyword(name="测试关键词1"),
        Keyword(name="测试关键词2"),
        Keyword(name="测试关键词3"),
    ]
    with transaction(db):
        for kw in keywords:
            db.add(kw)
    for kw in keywords:
        db.refresh(kw)
    yield keywords
    with transaction(db):
        for kw in keywords:
            db.delete(kw)


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
        file_path=await save_uploaded_file(file=pdf_file),
        file_type="pdf",
        subject_id=1,
        keyword_ids=[k.id for k in sample_keywords[:2]],
    )
    document = create_doc_service(doc=doc, db=db)
    assert document is not None
    yield document
    delete_doc_service(doc_id=document.id, db=db)
