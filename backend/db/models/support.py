from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column
from db.common import Base
from db.common import N_DIM, V_DIM
from pgvector.sqlalchemy import Vector, SPARSEVEC


class SupportModel(Base):
    """부산대 학지시"""

    __tablename__ = "supports"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    category = mapped_column(String, nullable=False)
    sub_category = mapped_column(String, nullable=True)

    title = mapped_column(String, nullable=False)
    url = mapped_column(String, nullable=False, unique=True)
    content = mapped_column(String, nullable=False)

    title_vector = mapped_column(Vector(dim=N_DIM), nullable=True)
    title_sparse_vector = mapped_column(SPARSEVEC(dim=V_DIM), nullable=True)

    content_chunks = relationship("SupportChunkModel", back_populates="support")
    attachments = relationship("SupportAttachmentModel", back_populates="support")


class SupportChunkModel(Base):
    """부산대 학지시 세부사항 chunk"""

    __tablename__ = "support_content_chunks"

    chunk_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    support_id = mapped_column(ForeignKey("supports.id", ondelete="CASCADE"))
    chunk_content = mapped_column(String, nullable=False)
    chunk_vector = mapped_column(Vector(dim=N_DIM), nullable=True)
    chunk_sparse_vector = mapped_column(SPARSEVEC(dim=V_DIM), nullable=True)

    support = relationship("SupportModel", back_populates="content_chunks")


class SupportAttachmentModel(Base):
    """학지시 각 항목 첨부파일 테이블"""

    __tablename__ = "support_attachments"

    attachment_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    support_id = mapped_column(ForeignKey("supports.id", ondelete="CASCADE"))
    name = mapped_column(String, nullable=False)
    url = mapped_column(String, nullable=False)

    support = relationship("SupportModel", back_populates="attachments")
