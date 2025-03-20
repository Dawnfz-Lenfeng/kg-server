from sqlalchemy.ext.asyncio import AsyncSession

from ..database import transaction
from ..models import Document
from ..schemas.keyword import KeywordCreate
from ..schemas.subject import Subject
from .document import DocService
from .keyword import KeywordService


class DocKeywordService:
    """处理文档和关键词之间的关联关系"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.doc_svc = DocService(db)
        self.kw_svc = KeywordService(db)

    async def create_keywards_for_doc(
        self, doc_id: int, keyword_names: list[str], subject: Subject
    ) -> Document | None:
        """从文本导入关键词并关联到文档"""
        doc = await self.doc_svc.get_doc(doc_id)
        if doc is None:
            return None

        new_keywords = set()
        for name in keyword_names:
            keyword = await self.kw_svc.get_keyword_by_name(name)
            if keyword is None:
                keyword = await self.kw_svc.create_keyword(
                    KeywordCreate(name=name, subject=subject)
                )
            new_keywords.add(keyword)

        await self.db.refresh(doc, ["keywords"])
        async with transaction(self.db):
            doc.keywords |= new_keywords

        await self.db.refresh(doc)
        return doc
