from typing import List
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.common import Base
from db.models.professor import ProfessorModel


class MajorModel(Base):
    __tablename__ = "majors"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, primary_key=True, autoincrement=True)
    minors: Mapped[List["MinorModel"]] = relationship(back_populates="major")

    professors: Mapped[List["ProfessorModel"]] = relationship(back_populates="major")


class MinorModel(Base):
    __tablename__ = "minors"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    minor_id = mapped_column(ForeignKey("minors.id"))
    name = mapped_column(String, primary_key=True, autoincrement=True)
    major: Mapped["MajorModel"] = relationship(back_populates="minors")

    professors: Mapped[List["ProfessorModel"]] = relationship(back_populates="minor")
