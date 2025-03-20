from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Edge(Base):
    __tablename__ = "edges"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[int] = mapped_column(nullable=False)
    target: Mapped[int] = mapped_column(nullable=False)
    weight: Mapped[float] = mapped_column(nullable=True)
