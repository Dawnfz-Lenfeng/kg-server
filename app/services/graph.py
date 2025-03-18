from typing import Sequence

from kgtools.graph import build_graph as build_relation_matrix
from kgtools.schemas.graph import GraphConfig
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..database import transaction
from ..models import Edge, Keyword
from ..schemas.graph import EdgeBase


class GraphService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def build_graph(
        self, docs: list[str], keywords: Sequence[Keyword], graph_config: GraphConfig
    ):
        """构建知识图谱并存入数据库"""
        keyword_names = [keyword.name for keyword in keywords]

        relation_matrix = build_relation_matrix(
            docs, keyword_names, **graph_config.model_dump()
        )

        rows, cols = relation_matrix.nonzero()
        edges = [
            Edge(
                source=keywords[i].id,
                target=keywords[j].id,
                weight=relation_matrix[i, j],
            )
            for i, j in zip(rows, cols)
        ]

        async with transaction(self.db):
            # 清除旧的图数据
            await self.db.execute(delete(Edge))

            for edge in edges:
                self.db.add(edge)
            await self.db.commit()

    async def get_graph(self):
        """从数据库中提取知识图谱"""
        result = await self.db.execute(select(Edge))
        edges = result.scalars().all()

        return [
            EdgeBase(source=edge.source, target=edge.target, weight=edge.weight)
            for edge in edges
        ]
