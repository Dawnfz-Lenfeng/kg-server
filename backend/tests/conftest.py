from io import BytesIO
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.schemas.document import DocCreate
from app.schemas.keyword import KeywordCreate
from app.services import DocService, KeywordService

SAMPLES_DIR = Path(__file__).parent / "samples"
TEST_DB_PATH = Path(__file__).parent / "test.db"
SQLALCHEMY_TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = async_sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """设置测试数据库"""
    from app import models

    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest_asyncio.fixture
async def db():
    """创建测试数据库会话"""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def doc_svc(db: AsyncSession):
    """创建文档服务实例"""
    return DocService(db)


@pytest.fixture
def kw_svc(db: AsyncSession):
    """创建关键词服务实例"""
    return KeywordService(db)


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
async def sample_keywords(kw_svc: KeywordService):
    """创建测试用关键词"""
    keyword_ids: list[int] = []

    for i in range(3):
        kw = await kw_svc.create_keyword(KeywordCreate(name=f"Keyword{i}"))
        keyword_ids.append(kw.id)

    yield keyword_ids

    for kw_id in keyword_ids:
        await kw_svc.delete_keyword(kw_id)


@pytest_asyncio.fixture
async def uploaded_file_name(pdf_file: UploadFile) -> str:
    from app.dependencies.documents import _save_uploaded_file

    return await _save_uploaded_file(file=pdf_file)


@pytest_asyncio.fixture
async def sample_doc(
    sample_keywords: list[int],
    uploaded_file_name: str,
    doc_svc: DocService,
):
    """创建测试文档"""
    doc = DocCreate(
        title="测试文档",
        file_name=uploaded_file_name,
        file_type="pdf",
        subject_id=1,
        keyword_ids=sample_keywords[:2],
    )
    document = await doc_svc.create_doc(doc)
    assert document is not None
    yield document.id
    await doc_svc.delete_doc(document.id)
