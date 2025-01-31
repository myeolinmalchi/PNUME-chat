from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, mapped_column
from db.common import Base


class UniversityModel(Base):
    """단과대학 테이블"""

    __tablename__ = "universities"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=False)
    departments = relationship("DepartmentModel", back_populates="university")


class DepartmentModel(Base):
    """학과 테이블"""

    __tablename__ = "departments"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    university_id = mapped_column(ForeignKey("universities.id"))
    name = mapped_column(String, nullable=False)
    university = relationship("UniversityModel", back_populates="departments")

    majors = relationship("MajorModel", back_populates="department")
    professors = relationship("ProfessorModel", back_populates="department")
    notices = relationship("NoticeModel", back_populates="department")
    buildings = relationship("BuildingModel", back_populates="department")

    subjects = relationship("SubjectModel", back_populates="department")


class MajorModel(Base):
    """세부 전공 테이블"""

    __tablename__ = "majors"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=False)
    department_id = mapped_column(ForeignKey("departments.id"))

    department = relationship("DepartmentModel", back_populates="majors")
    professors = relationship("ProfessorModel", back_populates="major")


class BuildingModel(Base):
    """대학 건물 테이블"""

    __tablename__ = "buildings"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=False, unique=True)
    building_num = mapped_column(Integer, nullable=False, unique=True)

    longitude = mapped_column(Float, nullable=False)
    latitude = mapped_column(Float, nullable=False)

    department_id = mapped_column(ForeignKey("departments.id"))
    department = relationship("DepartmentModel", back_populates="buildings")
    timetables = relationship("CourseTimeTableModel", back_populates="building")
