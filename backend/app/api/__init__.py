from fastapi import APIRouter

from .documents import router as documents_router

# from .keywords import router as keywords_router
# from .graph import router as graph_router

api_router = APIRouter()

api_router.include_router(documents_router)
# api_router.include_router(keywords_router, prefix="/keywords", tags=["keywords"])
# api_router.include_router(graph_router, prefix="/graph", tags=["graph"])
