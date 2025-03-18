from pydantic import BaseModel, ConfigDict

from .subject import Subject


class NodeData(BaseModel):
    name: str
    subject: Subject


class NodeBase(BaseModel):
    id: int
    data: NodeData


class EdgeBase(BaseModel):
    id: int
    source: int
    target: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class GraphBase(BaseModel):
    nodes: list[NodeBase]
    edges: list[EdgeBase]
