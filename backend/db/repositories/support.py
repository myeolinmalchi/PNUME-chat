from typing import Dict, List, NotRequired, Optional, TypedDict, Unpack
from db.models.support import SupportModel, SupportChunkModel
from db.repositories.base import BaseRepository
from pgvector.sqlalchemy import SparseVector
from db.common import V_DIM
from sqlalchemy import func, and_


class SupportRepository(BaseRepository[SupportModel]):

    def search_supports_content_hybrid(
        self,
        dense_vector: List[float],
        sparse_vector: Dict[int, float],
        lexical_ratio: float = 0.5,
        k: int = 5,
    ):
        """내용으로 유사도 검색"""
        score_dense = 1 - SupportChunkModel.chunk_vector.max_inner_product(dense_vector)
        score_lexical = -1 * (
            SupportChunkModel.chunk_sparse_vector.max_inner_product(
                SparseVector(sparse_vector, V_DIM)
            )
        )

        score = func.max((score_lexical * lexical_ratio) + score_dense *
                         (1 - lexical_ratio)).label("score")

        query = (
            self.session.query(SupportModel, SupportChunkModel, score).join(
                SupportModel, SupportModel.id == SupportChunkModel.support_id
            ).group_by(SupportChunkModel.id).group_by(SupportModel.id).order_by(score.desc()
                                                                                ).limit(k)
        )

        return query.all()

    def search_supports_hybrid(
        self,
        dense_vector: Optional[List[float]] = None,
        sparse_vector: Optional[Dict[int, float]] = None,
        lexical_ratio: float = 0.5,
        rrf_k: int = 120,
        k: int = 5,
        **kwargs
    ):

        score_dense_content = 1 - SupportChunkModel.chunk_vector.cosine_distance(dense_vector)
        score_lexical_title = -1 * (
            SupportChunkModel.chunk_sparse_vector.max_inner_product(
                SparseVector(sparse_vector, V_DIM)
            )
        )
        score_content = func.max((score_lexical_title * lexical_ratio) + score_dense_content *
                                 (1 - lexical_ratio)).label("score_content")

        rank_content = (
            self.session.query(
                SupportModel.id,
                func.row_number().over(order_by=score_content.desc()).label("rank_content"),
            ).join(SupportChunkModel, SupportModel.id == SupportChunkModel.support_id).group_by(
                SupportModel.id
            ).order_by(score_content.desc()).subquery()
        )

        score_dense_title = 1 - SupportModel.title_vector.cosine_distance(dense_vector)
        score_lexical_title = -1 * (
            SupportModel.title_sparse_vector.max_inner_product(SparseVector(sparse_vector, V_DIM))
        )
        score_title = ((score_lexical_title * lexical_ratio) + score_dense_title *
                       (1 - lexical_ratio)).label("score_title")

        rank_title = self.session.query(
            SupportModel.id,
            func.row_number().over(order_by=score_title.desc()).label("rank_title"),
        ).subquery()

        rrf_score = (
            1 / (rrf_k + rank_content.c.rank_content) + 1 / (rrf_k + rank_title.c.rank_title)
        ).label("rrf_score")

        query = (
            self.session.query(SupportModel).join(
                rank_content, SupportModel.id == rank_content.c.id
            ).join(rank_title,
                   SupportModel.id == rank_title.c.id).order_by(rrf_score.desc()).limit(k)
        )

        return query.all()
