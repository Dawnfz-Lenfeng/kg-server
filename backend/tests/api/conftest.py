import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

settings.TESTING = True

from app.database import get_db
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def override_dependency(db: AsyncSession):
    """覆盖应用中的 get_db 依赖，使用测试中的 db 会话"""

    async def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture
async def client():
    """创建异步测试客户端"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://testserver{settings.API_V1_STR}",
    ) as test_client:
        yield test_client
