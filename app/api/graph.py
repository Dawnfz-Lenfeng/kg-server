from fastapi import APIRouter, Body, Depends, HTTPException, Query
from kgtools.kgtools.graph.build_graph import build_graph
from ..schemas.graph import GraphBase, GraphBuildResult
from ..services import GraphService
from ..dependencies.graph import get_graph_svc

router = APIRouter(prefix="/graph", tags=["graph"])


@router.post("/build", response_model=GraphBuildResult)
async def build_graph(
    graph_svc: GraphService = Depends(get_graph_svc),
) -> GraphBuildResult:
    """构建知识图谱"""
    try:
        graph = await graph_svc.build_graph()
        return GraphBuildResult(
            success=True, error=None, model_config=graph.model_config
        )
    except Exception as e:
        return GraphBuildResult(success=False, error=str(e), model_config=None)


@router.get("/extract", response_model=GraphBase)
async def extract_graph(graph_svc: GraphService = Depends(get_graph_svc)) -> GraphBase:
    """提取知识图谱"""
    graph = await graph_svc.extract_graph()
    if graph is None:
        raise HTTPException(status_code=404, detail="Graph not found")
    return graph
