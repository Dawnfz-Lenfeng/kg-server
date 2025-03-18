from fastapi import APIRouter

from .auth import router as auth_router
from .documents import router as documents_router
from .graph import router as graph_router
from .keywords import router as keywords_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(documents_router)
api_router.include_router(keywords_router)
api_router.include_router(graph_router)
