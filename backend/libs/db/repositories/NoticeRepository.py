from typing import List
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
    ):
        """내용으로 유사도 검색"""
        similarity = Notice.content_vector.cosine_distance(query_encoding).label(
            "similarity"
        )
        return (
            self.session.query(Notice, similarity)
            .filter(similarity > threshold)
            .order_by("similarity")
            .limit(k)
            .all()
        )