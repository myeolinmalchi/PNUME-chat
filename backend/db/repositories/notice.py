from typing import Dict, List, NotRequired, Optional, TypedDict, Unpack

from pgvector.sqlalchemy import SparseVector
from sqlalchemy import Integer, cast, desc, func, and_, or_
from db.models import NoticeModel, NoticeChunkModel, DepartmentModel
from db.common import V_DIM
from db.models.calendar import SemesterModel
from services.base.types.calendar import DateRangeType
from .base import BaseRepository


class NoticeSearchFilterType(TypedDict, total=False):
    year: int
    departments: List[str]
    date_ranges: List[DateRangeType]
    categories: List[str]
    semester_ids: NotRequired[List[int]]


class NoticeRepository(BaseRepository[NoticeModel]):

    def _get_filters(self, **kwargs: Unpack[NoticeSearchFilterType]):
        filters = []
        if "year" in kwargs:
            year = kwargs["year"]
            filters.append(NoticeModel.date >= f"{year}-01-01 00:00:00")
            filters.append(NoticeModel.date < f"{year + 1}-01-01 00:00:00")

        if "semester_ids" in kwargs:
            semester_ids = kwargs['semester_ids']
            filters.append(NoticeModel.semester_id.in_(semester_ids))

        if "date_ranges" in kwargs:
            date_ranges = kwargs["date_ranges"]
            if date_ranges and len(date_ranges) > 0:
                date_filters = []
                for _range in kwargs["date_ranges"]:
                    st_date = _range["st_date"]
                    ed_date = _range["ed_date"]

                    date_filters.append(
                        and_(
                            NoticeModel.date >= st_date, NoticeModel.date
                            <= ed_date
                        )
                    )

                if len(date_filters) == 1:
                    filters.append(date_filters[0])

                elif len(date_filters) > 1:
                    filters.append(or_(*date_filters))

        if "departments" in kwargs:
            departments = kwargs["departments"]

            if departments and len(departments) > 0:
                dp = self.session.query(DepartmentModel).filter(
                    DepartmentModel.name.in_(departments)
                ).all()
                dp_ids = list(map(lambda d: d.id, dp))
                filters.append(NoticeModel.department_id.in_(dp_ids))

        return and_(*filters)

    def update_semester(
        self,
        semester: SemesterModel,
        batch: Optional[int] = None,
        offset: Optional[int] = None
    ):
        st, ed = semester.st_date, semester.ed_date
        date_filter = and_(NoticeModel.date >= st, NoticeModel.date <= ed)
        query = self.session.query(NoticeModel).filter(date_filter)
        if batch:
            query.limit(batch)
        if offset:
            query.offset(offset)

        notices = query.all()

        for notice in notices:
            setattr(notice, "semester_id", semester.id)
            self.session.flush()

        return notices

    def search_total_records(self, **kwargs: Unpack[NoticeSearchFilterType]):
        filter = self._get_filters(**kwargs)
        count = self.session.query(NoticeModel).filter(filter).count()
        return count

    # TODO: 기계공학부 로직 분리 필요
    def find_last_notice(self, **kwargs: Unpack[NoticeSearchFilterType]):
        filter = self._get_filters(**kwargs)

        notice_id = cast(func.split_part(NoticeModel.url, '/', 7),
                         Integer).label("notice_id")

        last_notice = self.session.query(NoticeModel,
                                         notice_id).where(filter).order_by(
                                             desc(notice_id)
                                         ).first()

        return last_notice[0] if last_notice else None

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

    def search_notices_title_hybrid(
        self,
        dense_vector: List[float],
        sparse_vector: Dict[int, float],
        lexical_ratio: float = 0.5,
        k: int = 10,
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
        rrf_k: int = 120,
        k: int = 5,
        **kwargs: Unpack[NoticeSearchFilterType]
    ):
        """제목 및 내용으로 유사도 검색"""

        filter = self._get_filters(**kwargs)

        score_dense_content = 1 - NoticeChunkModel.chunk_vector.cosine_distance(
            dense_vector
        )
        score_lexical_title = -1 * (
            NoticeChunkModel.chunk_sparse_vector.max_inner_product(
                SparseVector(sparse_vector, V_DIM)
            )
        )
        score_content = func.max((score_lexical_title * lexical_ratio) +
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
        score_lexical_title = -1 * (
            NoticeModel.title_sparse_vector.max_inner_product(
                SparseVector(sparse_vector, V_DIM)
            )
        )
        score_title = ((score_lexical_title * lexical_ratio) +
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
            ).join(rank_title,
                   NoticeModel.id == rank_title.c.id).filter(filter).order_by(
                       rrf_score.desc()
                   ).limit(k)
        )

        return query.all()
