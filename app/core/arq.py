from arq.connections import RedisSettings
from kgtools.schemas.preprocessing import ExtractConfig, NormalizeConfig

from ..database import AsyncSessionLocal
from ..services.document import DocService
from ..settings import settings


async def extract_doc(ctx, doc_id: int, config: ExtractConfig):
    """文档提取任务"""
    async with AsyncSessionLocal() as db:
        doc_service = DocService(db)
        await doc_service.extract_doc(doc_id, config)


async def normalize_doc(ctx, doc_id: int, config: ExtractConfig):
    """文档标准化任务"""
    async with AsyncSessionLocal() as db:
        doc_service = DocService(db)
        await doc_service.normalize_doc(doc_id, config)


class WorkerSettings:
    """Arq Worker 配置"""

    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        database=settings.REDIS_DB,
    )
    functions = [extract_doc, normalize_doc]
