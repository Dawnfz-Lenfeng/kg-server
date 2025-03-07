from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Graph(Base):
    __tablename__ = "graphs"

    source_id: Mapped[int] = mapped_column(nullable=False)
    target_id: Mapped[int] = mapped_column(nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
