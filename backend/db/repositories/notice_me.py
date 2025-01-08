from typing import Dict, List, Optional

from pgvector.sqlalchemy import SparseVector
from sqlalchemy import func
from db.models import NoticeModel, NoticeChunkModel
from db.common import V_DIM
from .base import BaseRepository


class NoticeMERepository(BaseRepository[NoticeModel]):

    def search_notices_title_hybrid(
        self,
        query_vector: List[float],
        query_sparse_vector: Dict[int, float],
        lexical_ratio: float = 0.5,
        k: int = 5,
    ):
        """제목으로 유사도 검색"""
        score_dense = 1 - NoticeModel.title_vector.cosine_distance(query_vector)
        score_lexical = -1 * (
            NoticeModel.title_sparse_vector.max_inner_product(
                SparseVector(query_sparse_vector, V_DIM)
            )
        )
        score = (
            (score_lexical * lexical_ratio) + score_dense * (1 - lexical_ratio)
        ).label("score")

        query = self.session.query(NoticeModel).order_by(score.desc()).limit(k)

        return query.all()

    def search_notices_content_hybrid(
        self,
        query_vector: List[float],
        query_sparse_vector: Dict[int, float],
        lexical_ratio: float = 0.5,
        k: int = 5,
    ) -> List[NoticeModel]:
        """내용으로 유사도 검색"""
        score_dense = 1 - NoticeChunkModel.chunk_vector.cosine_distance(query_vector)
        score_lexical = -1 * (
            NoticeChunkModel.chunk_sparse_vector.max_inner_product(
                SparseVector(query_sparse_vector, V_DIM)
            )
        )
        score = func.max(
            (score_lexical * lexical_ratio) + score_dense * (1 - lexical_ratio)
        ).label("score")

        query = (
            self.session.query(NoticeModel)
            .join(NoticeChunkModel, NoticeModel.id == NoticeChunkModel.notice_id)
            .group_by(NoticeModel.id)
            .order_by(score.desc())
            .limit(k)
        )

        return query.all()

    def search_notices_hybrid(
        self,
        dense_vector: Optional[List[float]] = None,
        sparse_vector: Optional[Dict[int, float]] = None,
        lexical_ratio: float = 0.5,
        rrf_k: int = 60,
        k: int = 5,
    ):
        score_dense_content = 1 - NoticeChunkModel.chunk_vector.cosine_distance(
            dense_vector
        )
        score_lexical_content = -1 * (
            NoticeChunkModel.chunk_sparse_vector.max_inner_product(
                SparseVector(sparse_vector, V_DIM)
            )
        )
        score_content = func.max(
            (score_lexical_content * lexical_ratio)
            + score_dense_content * (1 - lexical_ratio)
        ).label("score_content")

        rank_content = (
            self.session.query(
                NoticeModel.id,
                func.row_number()
                .over(order_by=score_content.desc())
                .label("rank_content"),
            )
            .join(NoticeChunkModel, NoticeModel.id == NoticeChunkModel.notice_id)
            .group_by(NoticeModel.id)
            .order_by(score_content.desc())
            .subquery()
        )

        score_dense_title = 1 - NoticeModel.title_vector.cosine_distance(dense_vector)
        score_lexical_content = -1 * (
            NoticeModel.title_sparse_vector.max_inner_product(
                SparseVector(sparse_vector, V_DIM)
            )
        )
        score_title = (
            (score_lexical_content * lexical_ratio)
            + score_dense_title * (1 - lexical_ratio)
        ).label("score_title")

        rank_title = self.session.query(
            NoticeModel.id,
            func.row_number().over(order_by=score_title.desc()).label("rank_title"),
        ).subquery()

        rrf_score = (
            1 / (rrf_k + rank_content.c.rank_content)
            + 1 / (rrf_k + rank_title.c.rank_title)
        ).label("rrf_score")

        query = (
            self.session.query(NoticeModel, rrf_score)
            .join(rank_content, NoticeModel.id == rank_content.c.id)
            .join(rank_title, NoticeModel.id == rank_title.c.id)
            .order_by(rrf_score.desc())
            .limit(k)
        )

        return query.all()
