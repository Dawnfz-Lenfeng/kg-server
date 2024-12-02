import os
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import transaction
from ..models import Document, Keyword
from ..preprocessing import extract_text, normalize_text
from ..schemas.document import DocCreate, DocUpdate, FileType
from ..schemas.preprocessing import ExtractConfig, NormalizeConfig


class DocService:
    def __init__(self, db: Session):
        self.db = db

    def create_doc(self, doc: DocCreate) -> Document:
        """创建文档"""
        try:
            with transaction(self.db):
                db_doc = Document(
                    **doc.model_dump(exclude={"keyword_ids"}, exclude_unset=True)
                )

                if doc.keyword_ids:
                    stmt = select(Keyword).where(Keyword.id.in_(doc.keyword_ids))
                    keywords = set(self.db.execute(stmt).scalars().all())
                    db_doc.keywords = keywords

                self.db.add(db_doc)

            self.db.refresh(db_doc)
            return db_doc

        except Exception as e:
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)
            raise e

    def extract_doc_text(
        self, doc_id: int, extract_config: ExtractConfig
    ) -> Document | None:
        """提取文档文本"""
        doc = self.read_doc(doc_id)
        if doc is None:
            return None

        try:
            doc.raw_text = extract_text(
                doc.file_path,
                file_type=doc.file_type,
                **extract_config.model_dump(),
            )
            with transaction(self.db):
                self.db.add(doc)

            self.db.refresh(doc)
            return doc
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Text extracting failed: {str(e)}"
            ) from e

    def normalize_doc_text(
        self, doc_id: int, normalize_config: NormalizeConfig
    ) -> Document | None:
        """标准化文档文本"""
        doc = self.read_doc(doc_id)
        if doc is None:
            return None

        doc.normalized_text = normalize_text(
            doc.raw_text,
            **normalize_config.model_dump(),
        )

        with transaction(self.db):
            self.db.add(doc)

        self.db.refresh(doc)
        return doc

    def read_doc(self, doc_id: int) -> Document | None:
        """获取单个文档"""
        stmt = (
            select(Document)
            .where(Document.id == doc_id)
            .options(selectinload(Document.keywords))
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def read_docs(
        self, skip: int, limit: int, subject_id: int | None
    ) -> Sequence[Document]:
        """获取文档列表"""
        stmt = select(Document).options(selectinload(Document.keywords))
        if subject_id is not None:
            stmt = stmt.where(Document.subject_id == subject_id)
        stmt = stmt.offset(skip).limit(limit)
        result = self.db.execute(stmt)
        return result.scalars().all()

    def update_doc(self, doc_id: int, doc_update: DocUpdate) -> Document | None:
        """更新文档信息"""
        doc = self.read_doc(doc_id)
        if doc is None:
            return None

        with transaction(self.db):
            update_data = doc_update.model_dump(
                exclude={"keywords"}, exclude_unset=True
            )
            for key, value in update_data.items():
                setattr(doc, key, value)

            if doc_update.keywords is not None:
                keywords_update = doc_update.keywords

                if keywords_update.add:
                    stmt = select(Keyword).where(Keyword.id.in_(keywords_update.add))
                    keywords_to_add = set(self.db.execute(stmt).scalars().all())
                    doc.keywords |= keywords_to_add

                if keywords_update.remove:
                    stmt = select(Keyword).where(Keyword.id.in_(keywords_update.remove))
                    keywords_to_remove = set(self.db.execute(stmt).scalars().all())
                    doc.keywords -= keywords_to_remove

            self.db.add(doc)

        self.db.refresh(doc)
        return doc

    def delete_doc(self, doc_id: int) -> bool:
        """删除文档"""
        doc = self.read_doc(doc_id)
        if doc is None:
            return False

        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)

        with transaction(self.db):
            self.db.delete(doc)
        return True
