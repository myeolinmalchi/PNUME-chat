from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from enum import Enum
from pgvector.sqlalchemy import Vector, SPARSEVEC
from sqlalchemy.orm import relationship
from libs.db.common import N_DIM, V_DIM, Base


class UrlEnum(Enum):
    hakbunotice = "공지/학부"
    gradnotice = "공지/대학원"
    supervision = "공지/장학"
    notice = "공지/홍보"
    hakbunews = "학부 소식"
    media = "언론 속 학부"
    seminar = "세미나"
    recruit = "취업정보"


class Notice(Base):
    """
    공지 게시판의 게시글 정보를 저장하는 notice 테이블

    Attributes:
        title: 게시글 제목
        title_vector: dense vector of the title
        title_sparse_vector: sparse vector of the title

        content: 게시글 내용
        content_vector: dense vector of the content
        content_sparse_vector: sparse vector of the content
    """

    __tablename__ = "notice"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(Integer, unique=True)

    category = Column(SQLEnum(UrlEnum, nullable=False))

    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    author = Column(String, nullable=False)

    title_vector = Column(Vector(N_DIM))
    content_vector = Column(Vector(N_DIM))
    title_sparse_vector = Column(SPARSEVEC(V_DIM))
    content_sparse_vector = Column(SPARSEVEC(V_DIM))

    attachments = relationship("Attachment", back_populates="notice")


class Attachment(Base):
    """게시글의 첨부파일 테이블"""

    __tablename__ = "notice_attachment"

    attachment_id = Column(Integer, primary_key=True, autoincrement=True)
    notice_id = Column(Integer, ForeignKey("notice.id"))
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)

    notice = relationship("Notice", back_populates="attachments")
