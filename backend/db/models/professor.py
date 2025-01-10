from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from db.common import Base
from sqlalchemy import Enum as SQLEnum
from db.models.fields import MajorModel, MinorModel
from enum import Enum


class ProfessorModel(Base):
    __tablename__ = "professors"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)

    major_id = mapped_column(ForeignKey("majors.id"))
    minor_id = mapped_column(ForeignKey("minors.id"))

    name: Mapped[str] = mapped_column(String, nullable=False)
    name_eng: Mapped[str] = mapped_column(String, nullable=True)

    profile_img: Mapped[str] = mapped_column(String, nullable=True)
    office_phone: Mapped[str] = mapped_column(String, nullable=True)
    website: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True)
    lab_addr: Mapped[str] = mapped_column(String, nullable=True)

    major: Mapped["MajorModel"] = relationship(back_populates="professors")
    minor: Mapped["MinorModel"] = relationship(back_populates="professors")


class ResearchFieldModel(Base):
    """연구분야"""

    __tablename__ = "professor_research_fields"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    professor_id = mapped_column(ForeignKey("professors.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    professor: Mapped["ProfessorModel"] = relationship(back_populates="research_fields")


class EduTypeEnum(Enum):
    bachelor = "학사"
    master = "석사"
    doctor = "박사"


class EducationModel(Base):
    """학력"""

    __tablename__ = "professor_educations"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=False)
    edu_type = mapped_column(
        SQLEnum(EduTypeEnum, values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
    )
    professor_id = mapped_column(ForeignKey("professors.id"))
    professor: Mapped["ProfessorModel"] = relationship(back_populates="research_fields")


class CareerModel(Base):
    """경력"""

    __tablename__ = "professor_careers"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=False)
    professor_id = mapped_column(ForeignKey("professors.id"))
    professor: Mapped["ProfessorModel"] = relationship(back_populates="research_fields")
