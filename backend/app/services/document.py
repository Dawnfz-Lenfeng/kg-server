import os
from contextlib import contextmanager
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import transaction
from ..models import Document, Keyword
from ..preprocessing import extract_text, normalize_text
from ..schemas.document import DocCreate, DocStage, DocUpdate
from ..schemas.preprocessing import ExtractConfig, NormalizeConfig


class DocService:
    def __init__(self, db: Session):
        self.db = db

    def create_doc(self, doc: DocCreate) -> Document:
        """创建文档"""
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

    def extract_doc_text(
        self, doc_id: int, extract_config: ExtractConfig
    ) -> Document | None:
        """提取文档文本"""
        doc = self.read_doc(doc_id)
        if doc is None:
            return None

        text = extract_text(
            self._get_text_path(doc, DocStage.UPLOAD),
            file_type=doc.file_type,
            **extract_config.model_dump(),
        )

        with self._save_text(doc, DocStage.EXTRACTED) as f:
            f.write(text)

        with transaction(self.db):
            self.db.add(doc)

        self.db.refresh(doc)
        return doc

    def normalize_doc_text(
        self, doc_id: int, normalize_config: NormalizeConfig
    ) -> Document | None:
        """标准化文档文本"""
        doc = self.read_doc(doc_id)
        if doc is None or not doc.is_extracted:
            return None

        with open(
            self._get_text_path(doc, DocStage.EXTRACTED), "r", encoding="utf-8"
        ) as f:
            raw_text = f.read()

        normalized_text = normalize_text(
            raw_text,
            **normalize_config.model_dump(),
        )

        with self._save_text(doc, DocStage.NORMALIZED) as f:
            f.write(normalized_text)

        with transaction(self.db):
            self.db.add(doc)

        self.db.refresh(doc)
        return doc

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

    def read_doc_text(self, doc_id: int, stage: DocStage) -> str | None:
        """获取文档文本内容"""
        doc = self.read_doc(doc_id)
        if doc is None:
            return None

        if not getattr(doc, stage):
            return None

        with open(self._get_text_path(doc, stage), "r", encoding="utf-8") as f:
            return f.read()

    def delete_doc(self, doc_id: int) -> bool:
        """删除文档"""
        doc = self.read_doc(doc_id)
        if doc is None:
            return False

        for stage in list(DocStage):
            file_path = self._get_text_path(doc, stage)
            if os.path.exists(file_path):
                os.remove(file_path)

        with transaction(self.db):
            self.db.delete(doc)
        return True

    @contextmanager
    def _save_text(self, doc: Document, stage: DocStage):
        """文本处理上下文管理器

        处理文本文件的读写，并自动更新文档字数
        """
        if not getattr(doc, stage):
            setattr(doc, stage, True)

        file = None
        try:
            file_path = self._get_text_path(doc, stage)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file = open(file_path, "w", encoding="utf-8")
            yield file

        finally:
            if file is not None:
                file.close()
                if stage == DocStage.NORMALIZED:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read()
                        doc.word_count = len(text.split())

    def _get_text_path(self, doc: Document, stage: DocStage) -> str:
        return f"{stage.storage_dir}/{doc.file_name}"
