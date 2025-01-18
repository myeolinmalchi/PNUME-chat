from typing import List
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.common import Base


class UniversityModel(Base):
    """단과대학 테이블"""

    __tablename__ = "universities"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=False)
    departments: Mapped[List["DepartmentModel"]
                        ] = relationship(back_populates="university")


class DepartmentModel(Base):
    """학과 테이블"""

    __tablename__ = "departments"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    university_id = mapped_column(ForeignKey("universities.id"))
    name = mapped_column(String, nullable=False)
    university: Mapped["UniversityModel"] = relationship(
        back_populates="departments"
    )

    majors = relationship("MajorModel", back_populates="department")
    professors = relationship("ProfessorModel", back_populates="department")
    notices = relationship("NoticeModel", back_populates="department")


class MajorModel(Base):
    """세부 전공 테이블"""

    __tablename__ = "majors"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=False)
    department_id = mapped_column(ForeignKey("departments.id"))

    department = relationship("DepartmentModel", back_populates="majors")
    professors = relationship("ProfessorModel", back_populates="major")
