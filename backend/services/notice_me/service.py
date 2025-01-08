from typing import List

from pgvector.sqlalchemy import SparseVector

from db.common import V_DIM
from db.models import AttachmentModel, NoticeChunkModel, NoticeModel
from db.repositories import transaction, NoticeMERepository
from utils.embed import EmbedResult

from .dto import NoticeMEDTO
import logging


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
        _title_vectors = [
            (
                {
                    "title_sparse_vector": SparseVector(t["sparse"], V_DIM),
                    "title_vector": t["dense"],
                }
                if t is not None
                else None
            )
            for t in title_vectors
        ]

        _attachments = [
            [AttachmentModel(**att) for att in n["attachments"]]
            for n in notices
            if "attachments" in n
        ]

        for notice in notices:
            del notice["attachments"]

        _content_vectors = [
            (
                [
                    NoticeChunkModel(
                        chunk_content=cc["chunk"],
                        chunk_vector=cc["dense"],
                        chunk_sparse_vector=SparseVector(cc["sparse"], V_DIM),
                    )
                    for cc in (c if c is not None else [])
                ]
            )
            for c in content_vectors
        ]

        print(len(_content_vectors[0]))

        try:
            notice_models = [
                NoticeModel(
                    **notice,
                    **title_vector,
                    content_chunks=content_chunks,
                    attachments=attachments,
                    category=category
                )
                for notice, title_vector, attachments, content_chunks in zip(
                    notices, _title_vectors, _attachments, _content_vectors
                )
            ]

            # self.notice_repo.bulk_create(notice_models)
            self.notice_repo.create_all(notice_models)

        except Exception:
            logging.exception("Error has been occurred while create notices(me)")
