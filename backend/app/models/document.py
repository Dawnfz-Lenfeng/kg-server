from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .keyword import document_keywords

if TYPE_CHECKING:
    from .keyword import Keyword
    from .subject import Subject


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    file_path: Mapped[str] = mapped_column(nullable=False)
    file_type: Mapped[str] = mapped_column(nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    raw_text: Mapped[str | None] = mapped_column(Text, default=None)
    normalized_text: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now, nullable=False
    )

    subject: Mapped[Subject] = relationship(back_populates="documents")
    keywords: Mapped[set[Keyword]] = relationship(
        "Keyword",
        secondary=document_keywords,
        collection_class=set,
        back_populates="documents",
    )
