from typing import List

from pgvector.sqlalchemy import SparseVector

from db.common import V_DIM
from db.models import AttachmentModel, NoticeChunkModel, NoticeModel
from db.repositories import transaction, NoticeMERepository
from utils.embed import EmbedResult

from .dto import NoticeMEDTO


class NoticeMEService:
    def __init__(self, notice_repo: NoticeMERepository):
        self.notice_repo = notice_repo

    @transaction()
    def create_notices(
        self,
        category: str,
        notices: List[NoticeMEDTO],
        title_vectors: List[EmbedResult | None],
        content_vectors: List[List[EmbedResult] | None],
    ):
        attachments = [
            {"attachments": [AttachmentModel(*att) for att in n["attachments"]]}
            for n in notices
        ]

        _title_vectors = [
            {
                "title_sparse_vector": (
                    SparseVector(t["sparse"]) if t is not None else None
                )
            }
            for t in title_vectors
        ]

        _content_vectors = [
            {
                "content_chunks": (
                    [
                        NoticeChunkModel(
                            chunk_content=cc["chunk"],
                            chunk_vector=cc["dense"],
                            chunk_sparse_vector=SparseVector(cc["sparse"], V_DIM),
                        )
                        for cc in c
                    ]
                    if c is not None
                    else None
                )
            }
            for c in content_vectors
        ]

        notice_models = [
            NoticeModel(**n, **a, **t, **c, category=category)
            for n, a, t, c in zip(
                notices, attachments, _title_vectors, _content_vectors
            )
        ]

        try:
            self.notice_repo.create_all(notice_models)
        except Exception as e:
            print("Error has been occurred while create notices(me)")
            print(e)
