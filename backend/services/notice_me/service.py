from typing import NotRequired, Optional, TypedDict, Unpack
from pgvector.sqlalchemy import SparseVector

from db.common import V_DIM
from db.models import AttachmentModel, NoticeChunkModel, NoticeModel
from db.repositories import transaction, NoticeMERepository

import asyncio
from services.base import BaseService
from services.notice_me import NoticeMECrawler, NoticeMEEmbedder, NoticeMEDTO


class NoticeMEService(BaseService):

    def parse_info(self, dto):
        info = dto.get("info")
        return info if info else {}

    def parse_attachments(self, dto):
        attachments = dto.get("attachments")
        return {
            "attachments": [AttachmentModel(**att) for att in attachments]
        } if attachments else {}

    def parse_embeddings(self, dto):
        embeddings = dto.get("embeddings")
        return {
            "title_sparse_vector": SparseVector(
                embeddings["title_embeddings"]["sparse"], V_DIM
            ),
            "title_vector": embeddings["title_embeddings"]["dense"],
            "content_chunks": [
                NoticeChunkModel(
                    chunk_content=content_vector["chunk"],
                    chunk_vector=content_vector["dense"],
                    chunk_sparse_vector=SparseVector(
                        content_vector["sparse"], V_DIM
                    ),
                ) for content_vector in embeddings["content_embeddings"]
            ]
        } if embeddings else {}

    def __init__(
        self, notice_repo: NoticeMERepository,
        notice_embedder: NoticeMEEmbedder, notice_crawler: NoticeMECrawler
    ):
        self.notice_repo = notice_repo
        self.notice_embedder = notice_embedder
        self.notice_crawler = notice_crawler

    def dto2orm(self, dto: NoticeMEDTO) -> Optional[NoticeModel]:
        info = self.parse_info(dto)
        attachments = self.parse_attachments(dto)
        embeddings = self.parse_embeddings(dto)

        if not info:
            return None

        return NoticeModel(**info, **attachments, **embeddings, seq=dto["seq"])

    def orm2dto(self, orm: NoticeModel) -> NoticeMEDTO:
        ...

    @transaction()
    async def run_full_crawling_pipeline_async(self, **kwargs):

        models = []

        url_key = kwargs.get('url_key', '')
        seq = self.notice_crawler.scrape_last_seq(url_key=url_key)
        to = kwargs.get('to', 1)
        interval = kwargs.get('interval', 30)
        to = seq - interval if to == -1 else to

        from tqdm import tqdm

        pbar = tqdm(
            range(1, seq + 1, interval),
            total=seq,
            desc=f"[{url_key}]",
        )
        for st in pbar:
            ed = st + interval - 1
            notices = await self.notice_crawler.scrape_partial_async(
                list(range(st, ed + 1)), url_key=url_key
            )
            if kwargs.get('with_embeddings', True):
                notices = await self.notice_embedder.embed_all_async(
                    items=notices, interval=interval
                )

            notice_models = [self.dto2orm(n) for n in notices]
            notice_models = [n for n in notice_models if n]
            notice_models = self.notice_repo.create_all(notice_models)
            models += notice_models

            pbar.update(interval)
            pbar.set_postfix({
                'range': f"{st} ~ {ed}",
            })

            await asyncio.sleep(kwargs.get('delay', 0))

        return models

    class SearchOptions(TypedDict):
        lexical_ratio: NotRequired[float]

    def search_notices_with_filter(
        self, query: str, **opts: Unpack[SearchOptions]
    ):
        embed_result = self.notice_embedder._embed_query(query, chunking=False)

        search_results = self.notice_repo.search_notices_title_hybrid(
            dense_vector=embed_result["dense"],
            sparse_vector=embed_result["sparse"],
            lexical_ratio=opts.get("lexical_ratio", 0.5)
        )

        return search_results


def create_notice_me_service(
    notice_repo: Optional[NoticeMERepository] = None,
    notice_crawler: Optional[NoticeMECrawler] = None,
    notice_embedder: Optional[NoticeMEEmbedder] = None
):
    notice_repo = NoticeMERepository() if not notice_repo else notice_repo
    notice_crawler = NoticeMECrawler() if not notice_crawler else notice_crawler
    notice_embedder = NoticeMEEmbedder(
    ) if not notice_embedder else notice_embedder

    notice_service = NoticeMEService(
        notice_repo, notice_embedder, notice_crawler
    )

    return notice_service
