from typing import List

from pgvector.sqlalchemy import SparseVector

from db.common import V_DIM
from db.models import AttachmentModel, NoticeChunkModel, NoticeModel
from db.repositories import transaction, NoticeMERepository

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
    ):

        def get_notice_model(notice: NoticeMEDTO):
            notice_model = NoticeModel(category=category)
            if "info" in notice:
                notice_model.title = notice["info"]["title"]
                notice_model.content = notice["info"]["content"]
                notice_model.date = notice["info"]["date"]
                notice_model.author = notice["info"]["author"]

                if notice["info"]["attachments"] is not None:
                    notice_model.attachments = [
                        AttachmentModel(**att) for att in notice["info"]["attachments"]
                    ]

            if "embeddings" in notice:
                embeddings = notice["embeddings"]
                notice_model.title_sparse_vector = SparseVector(
                    embeddings["title_embeddings"]["sparse"], V_DIM
                )
                notice_model.title_vector = embeddings["title_embeddings"]["dense"]
                notice_model.content_chunks = [
                    NoticeChunkModel(
                        chunk_content=content_vector["chunk"],
                        chunk_vector=content_vector["dense"],
                        chunk_sparse_vector=SparseVector(
                            content_vector["sparse"], V_DIM
                        ),
                    )
                    for content_vector in embeddings["content_embeddings"]
                ]

            return notice_model

        try:
            notice_models = [get_notice_model(notice) for notice in notices]
            self.notice_repo.create_all(notice_models)

        except Exception:
            logging.exception("Error has been occurred while create notices(me)")
