from typing import Dict, List, Optional

from sqlalchemy import func
from libs.db.models.Notice import Notice
from libs.db.repositories.BaseRepository import BaseRepository


class NoticeRepository(BaseRepository[Notice]):
    def find_orderby_total_similarity(
        self,
        query_encoding: List,
        title_weight: float = 0.5,
        threshold: float = 0.7,
        k: int = 5,
    ):
        """제목과 내용 혼합하여 유사도 검색"""
        title_similarity = (
            Notice.title_vector.cosine_distance(query_encoding) * title_weight
        )
        content_similarity = Notice.content_vector.cosine_distance(query_encoding) * (
            1 - title_weight
        )
        computed_col = (title_similarity + content_similarity).label("similarity")

        return (
            self.session.query(Notice, computed_col)
            .filter(computed_col > threshold)
            .order_by("similarity")
            .limit(k)
            .all()
        )

    def find_orderby_title_similarity(
        self, query_encoding: List, threshold: float = 0.7, k: int = 5
    ):
        """제목으로 유사도 검색"""
        similarity = Notice.title_vector.cosine_distance(query_encoding).label(
            "similarity"
        )
        return (
            self.session.query(Notice, similarity)
            .filter(similarity > threshold)
            .order_by("similarity")
            .limit(k)
            .all()
        )

    def find_orderby_content_similarity(
        self, query_encoding: List, threshold: float = 0.7, k: int = 5
    ) -> List[Notice]:
        """내용으로 유사도 검색"""
        similarity = (
            1 - func.cosine_distance(Notice.content_vector, query_encoding)
        ).label("similarity")
        return (
            self.session.query(Notice)
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
    ) -> List[Notice]:
        score_title_dense = 1 - func.cosine_distance(Notice.title_vector, query_vector)
        score_content_dense = 1 - func.cosine_distance(
            Notice.content_vector, query_vector
        )
        score_title_lexical = -1 * (
            func.inner_product(Notice.title_sparse_vector, query_sparse_vector)
        )
        score_content_lexical = -1 * (
            func.inner_product(Notice.content_sparse_vector, query_sparse_vector)
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

        query = self.session.query(Notice).order_by(score.desc()).limit(k)

        return query.all()
