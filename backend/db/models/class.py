from typing import List
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.common import Base
from universities import UniversityModel, DepartmentModel, MajorModel

class LectureModel(Base):
    """학과별 수업 테이블
    
    Attributes:
        course: 개설 과정 (대학/대학원)
        type: 과목구분 (전공기초/전공필수/전공선택/교양 ..)"""
    
    __tablename__ = "lectures"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    university_id = mapped_column(ForeignKey("univesrities.id"))
    department_id = mapped_column(ForeignKey("departments.id"))
    name = mapped_column(String, nullable=False)
    course = mapped_column(String, nullable=False)
    type = mapped_column(String, nullable=False)
    
    university: Mapped["UniversityModel"] = relationship(
        back_populates="lectures"
    )
    department: Mapped["DepartmentModel"] = relationship(
        back_populates="lectures"
    )