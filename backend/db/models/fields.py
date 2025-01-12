from typing import List
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.common import Base


class MajorModel(Base):
    __tablename__ = "majors"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=False)
    minors: Mapped[List["MinorModel"]] = relationship(back_populates="major")

    professors = relationship("ProfessorModel", back_populates="major")


class MinorModel(Base):
    __tablename__ = "minors"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    major_id = mapped_column(ForeignKey("majors.id"))
    name = mapped_column(String, nullable=False)
    major: Mapped["MajorModel"] = relationship(back_populates="minors")

    professors = relationship("ProfessorModel", back_populates="minor")
