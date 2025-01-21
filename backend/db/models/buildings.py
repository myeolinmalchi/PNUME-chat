from typing import List, Optional
from sqlalchemy import ForeingKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.common import Base
from universities import UniversityModel, DepartmentModel, MajorModel

class BuildingModel(Base):
    """대학 건물 테이블"""
    
    __tablename__ = "buildings"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=False, unique=True)
    building_num = mapped_column(Integer, nullable=False, unique=True)

    university_id = mapped_column(ForeingKey("universities.id"))
    universitied: Mapped[List["UniversityModel"]] = relationship (
        back_populates="buildings"
    )

    department_id = mapped_column(ForeingKey=("departments.id"))
    department: Mapped[List["DepartmentModel"]] = relationship(
        back_populates="buildings"
    )
    
    major_id = mapped_column(ForeingKey=("majors.id"))
    majors: Mapped[List[MajorModel]] = relationship(
        back_populates="buildings"
    )