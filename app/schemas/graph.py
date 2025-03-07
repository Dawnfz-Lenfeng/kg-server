from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class EdgeBase(BaseModel):
    source: int
    target: int
    weight: Optional[float] = None


class GraphBase(BaseModel):
    edges: list[EdgeBase]


class GraphBuildResult(BaseModel):
    success: bool = Field(..., description="是否上传成功")
    error: Optional[str] = None
    graph: Optional[list[EdgeBase]] = None
