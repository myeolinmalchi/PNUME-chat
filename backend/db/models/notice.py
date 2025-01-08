from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from pgvector.sqlalchemy import Vector, SPARSEVEC
from enum import Enum
from sqlalchemy.orm import mapped_column, relationship, Mapped
from db.common import N_DIM, V_DIM, Base
from typing import List


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
    __tablename__ = "notices"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    seq = mapped_column(Integer, unique=True)

    category = Column(
        SQLEnum(UrlEnum, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    date = mapped_column(Date, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)

    title_vector = mapped_column(Vector(N_DIM))
    title_sparse_vector = mapped_column(SPARSEVEC(V_DIM))

    attachments: Mapped[List["AttachmentModel"]] = relationship(back_populates="notice")
    content_chunks: Mapped[List["NoticeChunkModel"]] = relationship(
        back_populates="notice"
    )


class NoticeChunkModel(Base):
    __tablename__ = "notice_content_chunks"

    chunk_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    notice_id = mapped_column(ForeignKey("notices.id"))
    chunk_content = mapped_column(String, nullable=False)
    chunk_vector = mapped_column(Vector(N_DIM))
    chunk_sparse_vector = mapped_column(SPARSEVEC(dim=V_DIM))

    notice: Mapped["NoticeModel"] = relationship(back_populates="content_chunks")


class AttachmentModel(Base):
    """게시글의 첨부파일 테이블"""

    __tablename__ = "notice_attachments"

    attachment_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    notice_id = mapped_column(ForeignKey("notices.id"))
    name = mapped_column(String, nullable=False)
    url = mapped_column(String, nullable=False)

    notice: Mapped["NoticeModel"] = relationship(back_populates="attachments")
