from pydantic import BaseModel, ConfigDict, Field


class NodeBase(BaseModel):
    """节点基础模型"""

    name: str
    id: int
    category: str


class EdgeBase(BaseModel):
    """边基础模型"""

    source: NodeBase
    target: NodeBase
    weight: float


class GraphBase(BaseModel):
    edges: list[EdgeBase]


class GraphBuildResult(BaseModel):
    success: bool = Field(..., description="是否上传成功")
    error: str | None = Field(None, description="错误信息")

    model_config = ConfigDict(from_attributes=True)
