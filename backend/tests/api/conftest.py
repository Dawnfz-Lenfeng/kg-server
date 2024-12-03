import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.config import settings

settings.TESTING = True

from app.database import get_db
from app.main import app

from ..conftest import TestingSessionLocal


async def override_get_db():
    async with TestingSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    """创建异步测试客户端"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://testserver{settings.API_V1_STR}",
    ) as test_client:
        yield test_client
