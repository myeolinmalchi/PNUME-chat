from datetime import datetime
from sqlalchemy import Date, ForeignKey, Index, String
from pgvector.sqlalchemy import Vector, SPARSEVEC
from sqlalchemy.orm import mapped_column, relationship, Mapped
from db.common import N_DIM, V_DIM, Base
from typing import List

from db.models.calendar import SemesterModel
from db.models.university import DepartmentModel


class NoticeModel(Base):
    __tablename__ = "notices"

    __table_args__ = (
        Index(
            'ix_notice_department_semester',
            'department_id',
            'semester_id',
        ),
    )

    url: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    category: Mapped[str] = mapped_column(String, nullable=False)

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=True
    )
    department: Mapped[DepartmentModel] = relationship(back_populates="notices")

    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=True)

    title_vector = mapped_column(Vector(N_DIM), nullable=True)
    title_sparse_vector = mapped_column(SPARSEVEC(V_DIM), nullable=True)

    attachments: Mapped[List["AttachmentModel"]
                        ] = relationship(back_populates="notice")
    content_chunks: Mapped[List["NoticeChunkModel"]
                           ] = relationship(back_populates="notice")

    semester_id: Mapped[int] = mapped_column(
        ForeignKey("semesters.id"), nullable=True
    )
    semester: Mapped[SemesterModel] = relationship(back_populates="notices")


class NoticeChunkModel(Base):
    __tablename__ = "notice_content_chunks"

    notice_id: Mapped[int] = mapped_column(
        ForeignKey("notices.id", ondelete="CASCADE"), index=True
    )
    chunk_content: Mapped[str] = mapped_column(String, nullable=False)
    chunk_vector = mapped_column(Vector(N_DIM))
    chunk_sparse_vector = mapped_column(SPARSEVEC(dim=V_DIM))

    notice: Mapped["NoticeModel"] = relationship(
        back_populates="content_chunks"
    )


class AttachmentModel(Base):
    """게시글의 첨부파일 테이블"""

    __tablename__ = "notice_attachments"

    notice_id = mapped_column(
        ForeignKey("notices.id", ondelete="CASCADE"), index=True
    )
    name = mapped_column(String, nullable=False)
    url = mapped_column(String, nullable=False)

    notice: Mapped["NoticeModel"] = relationship(back_populates="attachments")
