from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .keyword import Keyword, document_keywords
from .subject import Subject


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    file_path: Mapped[str] = mapped_column(nullable=False)
    file_type: Mapped[str] = mapped_column(nullable=False)
    origin_text: Mapped[str | None] = mapped_column(Text, default=None)
    processed_text: Mapped[str | None] = mapped_column(Text, default=None)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now, nullable=False
    )

    subject: Mapped[Subject] = relationship(back_populates="documents")
    keywords: Mapped[list[Keyword]] = relationship(
        secondary=document_keywords,
        back_populates="documents",
    )
