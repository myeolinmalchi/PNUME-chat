from typing import List
from pgvector.sqlalchemy import SPARSEVEC, Vector
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from db.common import N_DIM, V_DIM, Base
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

    fields: Mapped[List["ResearchFieldModel"]
                   ] = relationship(back_populates="professor")
    educations: Mapped[List["EducationModel"]
                       ] = relationship(back_populates="professor")
    careers: Mapped[List["CareerModel"]
                    ] = relationship(back_populates="professor")


class ResearchFieldModel(Base):
    """연구분야"""

    __tablename__ = "professor_research_fields"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    professor_id = mapped_column(ForeignKey("professors.id"))

    name: Mapped[str] = mapped_column(String, nullable=False)
    dense_vector = mapped_column(Vector(N_DIM), nullable=False)
    sparse_vector = mapped_column(SPARSEVEC(V_DIM), nullable=False)

    professor: Mapped["ProfessorModel"] = relationship(back_populates="fields")


class EduTypeEnum(Enum):
    bachelor = "학사"
    master = "석사"
    doctor = "박사"
    masterdocter = "석박사통합"


class EducationModel(Base):
    """학력"""

    __tablename__ = "professor_educations"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    professor_id = mapped_column(ForeignKey("professors.id"))

    name = mapped_column(String, nullable=False)
    edu_type = mapped_column(
        SQLEnum(
            EduTypeEnum, values_callable=lambda obj: [e.value for e in obj]
        ),
        nullable=True,
    )

    professor: Mapped["ProfessorModel"] = relationship(
        back_populates="educations"
    )


class CareerModel(Base):
    """경력"""

    __tablename__ = "professor_careers"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    professor_id = mapped_column(ForeignKey("professors.id"))

    name = mapped_column(String, nullable=False)
    dense_vector = mapped_column(Vector(N_DIM), nullable=False)
    sparse_vector = mapped_column(SPARSEVEC(V_DIM), nullable=False)

    professor: Mapped["ProfessorModel"] = relationship(back_populates="careers")


PROFESSOR_MODEL_MAP = {
    "fields": ResearchFieldModel,
    "educations": EducationModel,
    "careers": CareerModel
}
