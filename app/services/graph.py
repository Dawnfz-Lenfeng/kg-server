from kgtools.kgtools.graph.build_graph import build_graph
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.graph import Graph
from ..schemas.graph import EdgeBase
from ..database import transaction


class GraphService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def build_graph(self) -> list[EdgeBase]:
        """构建知识图谱并存入数据库"""
        graph_data = await build_graph()
        edges = graph_data.get("edges", [])

        async with transaction(self.db):
            for edge in edges:
                new_edge = Graph(
                    source=edge["source"],
                    target=edge["target"],
                    weight=edge.get("weight"),
                )
                self.db.add(new_edge)
            await self.db.commit()

        return await self.extract_graph()

    async def extract_graph(self) -> list[EdgeBase]:
        """从数据库中提取知识图谱"""
        result = await self.db.execute(select(Graph))
        edges = result.scalars().all()

        return [
            EdgeBase(source=edge.source, target=edge.target, weight=edge.weight)
            for edge in edges
        ]
