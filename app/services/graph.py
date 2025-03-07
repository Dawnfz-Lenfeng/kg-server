from kgtools.kgtools.graph.build_graph import build_graph
from ..schemas.graph import GraphBase
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import transaction


class GraphService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def build_graph(self) -> GraphBase | None:
        """构建知识图谱"""
        db_graph = await build_graph(self.db)
        try:
            async with transaction(self.db):
                self.db.add(db_graph)

            await self.db.refresh(db_graph)
            return db_graph

        except Exception as e:
            file_path = db_graph.upload_path
            file_path.unlink(missing_ok=True)
            raise e

    async def extract_graph(self) -> GraphBase | None:
        """提取知识图谱"""
        graph = await self.read_graph()
        text = extract_text()

        async with transaction(self.db):
            await graph.write_text(text)

        await self.db.refresh(graph)
        return graph

    async def read_graph(self) -> GraphBase | None:
        """读取知识图谱"""
        return await self.db.execute(select(GraphBase)).scalar()
