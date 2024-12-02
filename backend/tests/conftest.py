from io import BytesIO
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi import UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, transaction
from app.models import Keyword
from app.schemas.document import DocCreate
from app.services import DocService

SAMPLES_DIR = Path(__file__).parent / "samples"
TEST_DB_PATH = Path(__file__).parent / "test.db"
SQLALCHEMY_TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """设置测试数据库"""
    from app import models

    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    Base.metadata.create_all(bind=engine)
    yield

    engine.dispose()
    Base.metadata.drop_all(bind=engine)
    engine.pool.dispose()

    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture
def db():
    """创建测试数据库会话"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def doc_svc(db: Session):
    """创建文档服务实例"""
    return DocService(db)


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
        content = f.read()

    file_like = BytesIO(content)
    yield UploadFile(file=BytesIO(content), filename="sample.pdf")
    file_like.close()


@pytest.fixture
def pdf_files():
    """提供测试用PDF文件列表"""
    pdf_path = SAMPLES_DIR / "sample.pdf"
    with pdf_path.open("rb") as f:
        content = f.read()

    file_like = BytesIO(content)
    files = [
        UploadFile(
            file=BytesIO(content),
            filename=f"sample{i}.pdf",
        )
        for i in range(3)
    ]

    yield files
    file_like.close()


@pytest_asyncio.fixture
async def uploaded_file_path(pdf_file: UploadFile) -> str:
    from app.dependencies.documents import _save_uploaded_file

    return await _save_uploaded_file(file=pdf_file)


@pytest.fixture
def sample_doc(
    sample_keywords: list[Keyword],
    uploaded_file_path: str,
    doc_svc: DocService,
):
    """创建测试文档"""
    doc = DocCreate(
        title="测试文档",
        file_path=uploaded_file_path,
        file_type="pdf",
        subject_id=1,
        keyword_ids=[k.id for k in sample_keywords[:2]],
    )
    document = doc_svc.create_doc(doc)
    assert document is not None
    yield document
    doc_svc.delete_doc(document.id)
