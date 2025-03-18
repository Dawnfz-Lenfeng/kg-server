from arq import ArqRedis
from fastapi import APIRouter, Depends, HTTPException
from kgtools.schemas.graph import GraphConfig

from ..core.response import to_response
from ..dependencies.graph import get_graph_svc
from ..dependencies.redis import get_redis
from ..services import GraphService

router = APIRouter(prefix="/graph", tags=["graph"])


@router.post("/build")
@to_response
async def build_graph(
    redis: ArqRedis = Depends(get_redis),
):
    """构建知识图谱"""
    await redis.enqueue_job("build_graph", GraphConfig())


@router.get("")
@to_response
async def get_graph(
    graph_svc: GraphService = Depends(get_graph_svc),
):
    """提取知识图谱"""
    graph = await graph_svc.get_graph()
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")
    return graph
