import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.database import get_db
from app.main import app

from ..conftest import TestingSessionLocal


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """创建测试客户端"""
    with TestClient(
        app, base_url=f"http://testserver{settings.API_V1_STR}"
    ) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_client():
    """创建异步测试客户端"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://testserver{settings.API_V1_STR}",
    ) as test_client:
        yield test_client
