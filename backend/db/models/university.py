from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy import Table, Column
from db.common import Base, SQLEnum
from enum import Enum


class StructEnum(Enum):
    """구분(건물 구조)"""
    steel = "ST"
    light_steel = "경량ST"
    steel_reinforced_concrete = "SRC"
    reinforced_concrete = "RC"
    masonry = "석조"
    brick = "벽돌조"


class PlaceEnum(Enum):
    """구분(구내/외)"""
    onsite = "구내"
    offsite = "구외"


class SafetyEnum(Enum):
    """안전등급"""
    A = "A"
    B = "B"
    C = "C"


association_table = Table(
    "assiciation", Base.metadata, Column("department_id", ForeignKey("departments.id"), primary_key=True),
    Column("building_id", ForeignKey("buildings.id"), primary_key=True)
)


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
    buildings = relationship("BuildingModel", secondary=association_table, back_populates="department")

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

    place = mapped_column(SQLEnum(PlaceEnum), nullable=False)
    structure = mapped_column(SQLEnum(StructEnum), nullable=False)
    floor_under = mapped_column(Integer, nullable=False)
    floor_above = mapped_column(Integer, nullable=False)
    completion = mapped_column(String, nullable=False)
    building_area = mapped_column(Integer, nullable=False)
    total_floor_area = mapped_column(Integer, nullable=False)
    year_elapsed = mapped_column(Integer, nullable=False)
    safety = mapped_column(SQLEnum(SafetyEnum), nullable=False)

    longitude = mapped_column(Float, nullable=False)
    latitude = mapped_column(Float, nullable=False)

    main_department = mapped_column(String, nullable=False)

    university_id = mapped_column(ForeignKey("universities.id"))
    department_id = mapped_column(ForeignKey("departments.id"))

    department = relationship("DepartmentModel", secondary=association_table, back_populates="buildings")

    timetables = relationship("CourseTimeTableModel", back_populates="building")
