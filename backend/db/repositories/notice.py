from typing import Dict, List, NotRequired, Optional, TypedDict, Unpack

from pgvector.sqlalchemy import SparseVector
from sqlalchemy import func, and_
from db.models import NoticeModel, NoticeChunkModel, DepartmentModel
from db.common import V_DIM
from .base import BaseRepository


class NoticeSearchFilter(TypedDict):
    year: NotRequired[int]
    departments: NotRequired[List[str]]


class NoticeRepository(BaseRepository[NoticeModel]):

    def search_filter(self, **kwargs: Unpack[NoticeSearchFilter]):
        filters = []
        if "year" in kwargs:
            year = kwargs["year"]
            filters.append(NoticeModel.date >= f"{year}-01-01 00:00:00")
            filters.append(NoticeModel.date < f"{year + 1}-01-01 00:00:00")
        if "departments" in kwargs:
            departments = kwargs["departments"]
            dp = self.session.query(DepartmentModel).filter(
                DepartmentModel.name.in_(departments)
            ).all()
            dp_ids = list(map(lambda d: d.id, dp))
            filters.append(NoticeModel.department_id.in_(dp_ids))

        return and_(*filters)

    def find_last_notice(self, department: str, category: str):
        department_model = self.session.query(DepartmentModel).where(
            DepartmentModel.name == department
        ).limit(1).one_or_none()

        if not department_model:
            raise ValueError(f"({department}) 학과가 존재하지 않습니다.")

        last_notice = self.session.query(NoticeModel).where(
            NoticeModel.department_id == department_model.id
            and NoticeModel.category == category
        ).order_by(NoticeModel.url.desc()).limit(1).one_or_none()

        return last_notice
    def delete_by_department(self, department: str):
        department_model = self.session.query(DepartmentModel).filter(
            DepartmentModel.name == department
        ).one_or_none()
        if department_model is None:
            raise ValueError(f"존재하지 않는 학과입니다: {department}")

        affected = self.session.query(NoticeModel).filter(
            NoticeModel.department_id == department_model.id
        ).delete()

        return affected

    def create_all(self, objects):
        self.session.add_all(objects)
        self.session.flush()
        return objects

    def search_notices_title_hybrid(
        self,
        dense_vector: List[float],
        sparse_vector: Dict[int, float],
        lexical_ratio: float = 0.5,
        k: int = 5,
    ):
        """제목으로 유사도 검색"""
        score_dense = 1 - NoticeModel.title_vector.cosine_distance(dense_vector)
        score_lexical = -1 * (
            NoticeModel.title_sparse_vector.max_inner_product(
                SparseVector(sparse_vector, V_DIM)
            )
        )
        score = ((score_lexical * lexical_ratio) + score_dense *
                 (1 - lexical_ratio)).label("score")

        query = self.session.query(NoticeModel,
                                   score).order_by(score.desc()).limit(k)

        return query.all()

    def search_notices_content_hybrid(
        self,
        query_vector: List[float],
        query_sparse_vector: Dict[int, float],
        lexical_ratio: float = 0.5,
        k: int = 5,
    ) -> List[NoticeModel]:
        """내용으로 유사도 검색"""
        score_dense = 1 - NoticeChunkModel.chunk_vector.cosine_distance(
            query_vector
        )
        score_lexical = -1 * (
            NoticeChunkModel.chunk_sparse_vector.max_inner_product(
                SparseVector(query_sparse_vector, V_DIM)
            )
        )
        score = func.max((score_lexical * lexical_ratio) + score_dense *
                         (1 - lexical_ratio)).label("score")

        query = (
            self.session.query(NoticeModel).join(
                NoticeChunkModel, NoticeModel.id == NoticeChunkModel.notice_id
            ).group_by(NoticeModel.id).order_by(score.desc()).limit(k)
        )

        return query.all()

    def search_notices_hybrid(
        self,
        dense_vector: Optional[List[float]] = None,
        sparse_vector: Optional[Dict[int, float]] = None,
        lexical_ratio: float = 0.5,
        rrf_k: int = 60,
        k: int = 5,
        **kwargs
    ):

        filter = self.search_filter(**kwargs)
        #query = query.filter(filter).limit(k)

        score_dense_content = 1 - NoticeChunkModel.chunk_vector.cosine_distance(
            dense_vector
        )
        score_lexical_content = -1 * (
            NoticeChunkModel.chunk_sparse_vector.max_inner_product(
                SparseVector(sparse_vector, V_DIM)
            )
        )
        score_content = func.max((score_lexical_content * lexical_ratio) +
                                 score_dense_content *
                                 (1 - lexical_ratio)).label("score_content")

        rank_content = (
            self.session.query(
                NoticeModel.id,
                func.row_number().over(order_by=score_content.desc()
                                       ).label("rank_content"),
            ).join(
                NoticeChunkModel, NoticeModel.id == NoticeChunkModel.notice_id
            ).group_by(NoticeModel.id
                       ).filter(filter).order_by(score_content.desc()
                                                 ).subquery()
        )

        score_dense_title = 1 - NoticeModel.title_vector.cosine_distance(
            dense_vector
        )
        score_lexical_content = -1 * (
            NoticeModel.title_sparse_vector.max_inner_product(
                SparseVector(sparse_vector, V_DIM)
            )
        )
        score_title = ((score_lexical_content * lexical_ratio) +
                       score_dense_title *
                       (1 - lexical_ratio)).label("score_title")

        rank_title = self.session.query(
            NoticeModel.id,
            func.row_number().over(order_by=score_title.desc()
                                   ).label("rank_title"),
        ).filter(filter).subquery()

        rrf_score = (
            1 / (rrf_k + rank_content.c.rank_content) + 1 /
            (rrf_k + rank_title.c.rank_title)
        ).label("rrf_score")

        query = (
            self.session.query(NoticeModel, rrf_score).join(
                rank_content, NoticeModel.id == rank_content.c.id
            ).join(rank_title, NoticeModel.id == rank_title.c.id).order_by(
                rrf_score.desc()
            ).limit(k)
        )

        return query.all()
