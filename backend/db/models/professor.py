from typing import List
from pgvector.sqlalchemy import SPARSEVEC, Vector
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from db.common import N_DIM, V_DIM, Base
from sqlalchemy import Enum as SQLEnum
from enum import Enum


class ProfessorModel(Base):
    __tablename__ = "professors"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    url = mapped_column(String, nullable=False, unique=True)

    department_id = mapped_column(ForeignKey("departments.id"), nullable=False)
    major_id = mapped_column(ForeignKey("majors.id"), nullable=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    name_eng: Mapped[str] = mapped_column(String, nullable=True)

    profile_img: Mapped[str] = mapped_column(String, nullable=True)
    office_phone: Mapped[str] = mapped_column(String, nullable=True)
    website: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True)
    lab_addr: Mapped[str] = mapped_column(String, nullable=True)

    department = relationship("DepartmentModel", back_populates="professors")
    major = relationship("MajorModel", back_populates="professors")

    detail: Mapped[str] = mapped_column(String, nullable=True)
    detail_chunks: Mapped[List["ProfessorDetailChunkModel"]
                          ] = relationship(back_populates="professor")


class ProfessorDetailChunkModel(Base):
    __tablename__ = "professor_detail_chunks"

    chunk_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    professor_id = mapped_column(ForeignKey("professors.id"))

    detail = mapped_column(String, nullable=False)
    dense_vector = mapped_column(Vector(N_DIM))
    sparse_vector = mapped_column(SPARSEVEC(dim=V_DIM))

    professor: Mapped["ProfessorModel"] = relationship(
        back_populates="detail_chunks"
    )


'''
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
    dense_vector = mapped_column(Vector(N_DIM), nullable=False)
    sparse_vector = mapped_column(SPARSEVEC(V_DIM), nullable=False)

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
'''
