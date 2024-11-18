from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)

    documents = relationship("Document", back_populates="subject")
