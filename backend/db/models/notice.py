from sqlalchemy import Date, ForeignKey, Integer, String
from pgvector.sqlalchemy import Vector, SPARSEVEC
from sqlalchemy.orm import mapped_column, relationship, Mapped
from db.common import N_DIM, V_DIM, Base
from typing import List


class NoticeModel(Base):
    __tablename__ = "notices"

    url = mapped_column(String, nullable=False, unique=True)

    category = mapped_column(String, nullable=False)

    department_id = mapped_column(ForeignKey("departments.id"), nullable=True)
    department = relationship("DepartmentModel", back_populates="notices")

    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    date = mapped_column(Date, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=True)

    title_vector = mapped_column(Vector(N_DIM), nullable=True)
    title_sparse_vector = mapped_column(SPARSEVEC(V_DIM), nullable=True)

    attachments: Mapped[List["AttachmentModel"]
                        ] = relationship(back_populates="notice")
    content_chunks: Mapped[List["NoticeChunkModel"]
                           ] = relationship(back_populates="notice")

    semester_id: Mapped[int] = mapped_column(ForeignKey("semesters.id"), nullable=True)
    semester: Mapped[SemesterModel] = relationship(back_populates="notices")


class NoticeChunkModel(Base):
    __tablename__ = "notice_content_chunks"

    notice_id = mapped_column(ForeignKey("notices.id", ondelete="CASCADE"))
    chunk_content = mapped_column(String, nullable=False)
    chunk_vector = mapped_column(Vector(N_DIM))
    chunk_sparse_vector = mapped_column(SPARSEVEC(dim=V_DIM))

    notice: Mapped["NoticeModel"] = relationship(
        back_populates="content_chunks"
    )


class AttachmentModel(Base):
    """게시글의 첨부파일 테이블"""

    __tablename__ = "notice_attachments"

    notice_id = mapped_column(ForeignKey("notices.id", ondelete="CASCADE"))
    name = mapped_column(String, nullable=False)
    url = mapped_column(String, nullable=False)

    notice: Mapped["NoticeModel"] = relationship(back_populates="attachments")
