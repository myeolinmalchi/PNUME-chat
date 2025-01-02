from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from enum import Enum
from pgvector.sqlalchemy import Vector, SPARSEVEC
from sqlalchemy.orm import mapped_column, relationship
from db.database import N_DIM, V_DIM, Base


class UrlEnum(Enum):
    hakbunotice = "공지/학부"
    gradnotice = "공지/대학원"
    supervision = "공지/장학"
    notice = "공지/홍보"
    hakbunews = "학부 소식"
    media = "언론 속 학부"
    seminar = "세미나"
    recruit = "취업정보"


class NoticeModel(Base):
    """
    공지 게시판의 게시글 정보를 저장하는 notice 테이블

    Attributes:
        title: 게시글 제목
        title_vector: dense vector of the title
        title_sparse_vector: sparse vector of the title
        content: 게시글 내용
    """

    __tablename__ = "notices"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    key = mapped_column(Integer, unique=True)

    category = mapped_column(SQLEnum(UrlEnum, nullable=False))

    title = mapped_column(String, nullable=False)
    content = mapped_column(String, nullable=False)
    date = mapped_column(Date, nullable=False)
    author = mapped_column(String, nullable=False)

    title_vector = mapped_column(Vector(N_DIM))
    title_sparse_vector = mapped_column(SPARSEVEC(V_DIM))

    attachments = relationship("AttachmentModel", back_populates="notice")
    content_chunks = relationship("NoticeChunkModel", back_populates="notice")


class NoticeChunkModel(Base):
    __tablename__ = "notice_content_chunks"

    chunk_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    notice_id = mapped_column(Integer, ForeignKey("notices.id"))
    chunk_content = mapped_column(String, nullable=False)
    chunk_vector = mapped_column(Vector(N_DIM))
    chunk_sparse_vector = mapped_column(SPARSEVEC(dim=V_DIM))

    notice = relationship("NoticeModel", back_populates="content_chunks")


class AttachmentModel(Base):
    """게시글의 첨부파일 테이블"""

    __tablename__ = "notice_attachments"

    attachment_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    notice_id = mapped_column(Integer, ForeignKey("notices.id"))
    name = mapped_column(String, nullable=False)
    url = mapped_column(String, nullable=False)

    notice = relationship("NoticeModel", back_populates="attachments")
