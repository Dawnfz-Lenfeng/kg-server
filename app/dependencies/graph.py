from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.graph import GraphService


async def get_graph_svc(db: AsyncSession = Depends(get_db)) -> GraphService:
    return GraphService(db)
