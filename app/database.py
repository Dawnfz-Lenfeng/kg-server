from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .settings import settings

if settings.DEV_MODE:
    SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./dev.db"
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL 异步 URL 格式：postgresql+asyncpg://
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    )

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, autocommit=False, autoflush=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def transaction(session: AsyncSession):
    """异步事务上下文管理器"""
    try:
        yield
        await session.commit()
    except Exception:
        await session.rollback()
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    from . import models

    """初始化数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()
