from pydantic import BaseModel


class EdgeBase(BaseModel):
    source: int
    target: int
    weight: float | None = None
