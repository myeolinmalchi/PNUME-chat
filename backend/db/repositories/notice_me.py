from typing import Dict, List, Optional

from sqlalchemy import func
from db.models import NoticeModel
from .base import BaseRepository


class NoticeMERepository(BaseRepository[NoticeModel]):
    def find_orderby_total_similarity(
        self,
        query_encoding: List,
        title_weight: float = 0.5,
        threshold: float = 0.7,
        k: int = 5,
    ):
        """제목과 내용 혼합하여 유사도 검색"""
        title_similarity = (
            NoticeModel.title_vector.cosine_distance(query_encoding) * title_weight
        )
        content_similarity = NoticeModel.content_vector.cosine_distance(
            query_encoding
        ) * (1 - title_weight)
        computed_col = (title_similarity + content_similarity).label("similarity")

        return (
            self.session.query(NoticeModel, computed_col)
            .filter(computed_col > threshold)
            .order_by("similarity")
            .limit(k)
            .all()
        )

    def find_orderby_title_similarity(
        self, query_encoding: List, threshold: float = 0.7, k: int = 5
    ):
        """제목으로 유사도 검색"""
        similarity = NoticeModel.title_vector.cosine_distance(query_encoding).label(
            "similarity"
        )
        return (
            self.session.query(NoticeModel, similarity)
            .filter(similarity > threshold)
            .order_by("similarity")
            .limit(k)
            .all()
        )

    def find_orderby_content_similarity(
        self, query_encoding: List, threshold: float = 0.7, k: int = 5
    ) -> List[NoticeModel]:
        """내용으로 유사도 검색"""
        similarity = (
            1 - func.cosine_distance(NoticeModel.content_vector, query_encoding)
        ).label("similarity")
        return (
            self.session.query(NoticeModel)
            .filter(similarity > threshold)
            .order_by(similarity.desc())
            .limit(k)
            .all()
        )

    def search_orderby_weighted_sum(
        self,
        query_vector: Optional[List[float]] = None,
        query_sparse_vector: Optional[List[Dict[str, float]]] = None,
        lexical_ratio: float = 0.5,
        title_ratio: float = 0.5,
        k: int = 5,
    ) -> List[NoticeModel]:
        score_title_dense = 1 - func.cosine_distance(
            NoticeModel.title_vector, query_vector
        )
        score_content_dense = 1 - func.cosine_distance(
            NoticeModel.content_vector, query_vector
        )
        score_title_lexical = -1 * (
            func.inner_product(NoticeModel.title_sparse_vector, query_sparse_vector)
        )
        score_content_lexical = -1 * (
            func.inner_product(NoticeModel.content_sparse_vector, query_sparse_vector)
        )
        score_title = (score_title_lexical * lexical_ratio) + score_title_dense * (
            1 - lexical_ratio
        )
        score_content = (
            score_content_lexical * lexical_ratio
        ) + score_content_dense * (1 - lexical_ratio)

        score = (
            (score_title * title_ratio) + (score_content * (1 - title_ratio))
        ).label("score")

        query = self.session.query(NoticeModel).order_by(score.desc()).limit(k)

        return query.all()
