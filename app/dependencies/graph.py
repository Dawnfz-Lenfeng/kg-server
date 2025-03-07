import asyncio
import uuid
from pathlib import Path
from typing import cast
from urllib.parse import unquote

from fastapi import Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..schemas.graph import GraphBase
from ..services.graph import GraphService


async def get_graph_svc(db: AsyncSession = Depends(get_db)) -> GraphService:
    return GraphService(db)
