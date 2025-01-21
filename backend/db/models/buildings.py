from typing import List, Optional
from sqlalchemy import ForeingKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.common import Base

###단과 대학/학과 테이블 가져오기 
from universities import UniversityModel, DepartmentModel, MajorModel


###대학 건물 테이블
###단과 대학/학과 테이블이랑 one-to-many관계
####BuildingsModel Table이 uiversities파일에 있는 table의 자식 테이블이다. 즉 얘가 fk로 다른 talble의 pk를 가져간다.
class BuildingsModel(Base):
    """대학 건물 테이블"""
    
    __tablename__ = "buildings"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    ##단과 대학 
    university_id = mapped_column(ForeingKey("universities.id"))
    universitied: Mapped[List["UniversityModel"]] = relationship (
        back_populates="buildings"
    )


    ##학과 
    department_id = mapped_column(ForeingKey=("departments.id"))
    department: Mapped[List["DepartmentModel"]] = relationship(
        back_populates="buildings"
    )


    ##세부 전공
    major_id = mapped_column(ForeingKey=("majors.id"))
    majors: Mapped[List[MajorModel]] = relationship(
        back_populates="buildings"
    )
    
    ##건물이름  Ex) 경영관
    name = mapped_column(String, nullable=False, unique=True)
    ##building 번호 Ex) 경영관 = 514
    building_num = mapped_column(Integer, nullable=False, unique=True)