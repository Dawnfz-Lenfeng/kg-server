import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base


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
