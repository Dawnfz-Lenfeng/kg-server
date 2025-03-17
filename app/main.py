from contextlib import asynccontextmanager

from arq import create_pool
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .core.arq import WorkerSettings
from .database import lifespan as db_lifespan
from .settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    async with db_lifespan(app):
        redis_settings = WorkerSettings.redis_settings
        app.state.redis = await create_pool(redis_settings)
        yield
        await app.state.redis.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan if not settings.TESTING else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to CKGCUS API"}
