from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    real_name: Mapped[str]
    avatar: Mapped[str]
    desc: Mapped[str | None]
    role_name: Mapped[str]
    role_value: Mapped[str]
