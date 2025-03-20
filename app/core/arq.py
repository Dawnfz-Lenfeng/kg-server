import logging

from arq.connections import RedisSettings
from kgtools.schemas.graph import GraphConfig
from kgtools.schemas.preprocessing import ExtractConfig, NormalizeConfig

from ..database import AsyncSessionLocal
from ..schemas.document import DocState
from ..services import DocService, GraphService, KeywordService
from ..settings import settings

logger = logging.getLogger(__name__)


async def extract_doc(
    ctx,
    doc_id: int,
    config: ExtractConfig,
    current_state: DocState,
):
    """文档提取任务"""
    async with AsyncSessionLocal() as session:
        doc_svc = DocService(session)
        try:
            if current_state in {DocState.EXTRACTING, DocState.NORMALIZING}:
                raise ValueError("doc is already processing")
            await doc_svc.extract_doc(doc_id, config)
        except Exception as e:
            logger.error(f"extract doc {doc_id} failed: {e}")
            await doc_svc.update_doc_state(doc_id, current_state)


async def normalize_doc(
    ctx,
    doc_id: int,
    config: NormalizeConfig,
    current_state: DocState,
):
    """文档标准化任务"""
    async with AsyncSessionLocal() as session:
        doc_svc = DocService(session)
        try:
            if current_state not in {DocState.EXTRACTED, DocState.NORMALIZED}:
                raise ValueError("doc is not in extracted state")
            await doc_svc.normalize_doc(doc_id, config)
        except Exception as e:
            logger.error(f"normalize doc {doc_id} failed: {e}")
            await doc_svc.update_doc_state(doc_id, current_state)


async def build_graph(ctx, config: GraphConfig):
    """构建知识图谱任务"""
    try:
        async with AsyncSessionLocal() as session:
            doc_svc = DocService(session)
            docs = await doc_svc.get_docs()

            doc_texts = []
            for doc in docs:
                if doc.state != DocState.NORMALIZED:
                    logger.warning(f"doc {doc.id} is not normalized")
                    continue
                doc_text = await doc.read_text(DocState.NORMALIZED)
                doc_texts.append(doc_text)
            if not doc_texts:
                logger.warning("No normalized docs found")
                return

            kw_svc = KeywordService(session)
            keywords = await kw_svc.get_keywords()
            if not keywords:
                logger.warning("No keywords found in documents")
                return

            graph_svc = GraphService(session)
            await graph_svc.build_graph(doc_texts, keywords, config)

    except Exception as e:
        logger.error(f"build graph failed: {e}")


class WorkerSettings:
    """Arq Worker 配置"""

    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        database=settings.REDIS_DB,
    )
    functions = [extract_doc, normalize_doc, build_graph]
