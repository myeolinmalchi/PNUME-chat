from pgvector.sqlalchemy import SparseVector
from db.common import V_DIM
from db.models.support import SupportAttachmentModel, SupportChunkModel, SupportModel
from services.base.service import BaseService
from typing import Optional, TypedDict, NotRequired, Unpack
import json
from tqdm import tqdm
import asyncio

from services.support.dto import SupportDTO
import logging

from db.repositories import SupportRepository

logger = logging.getLogger(__name__)


class SupportService(BaseService):

    def __init__(self, support_repo, support_crawler, support_embedder):
        self.support_repo = support_repo
        self.support_crawler = support_crawler
        self.support_embedder = support_embedder

    def parse_info(self, dto):
        info = dto.get("info")
        return info if info else {}

    def parse_attachments(self, dto):
        attachments = dto.get("attachments")
        return {"attachments": [SupportAttachmentModel(**att) for att in attachments]} if attachments else {}

    def parse_embeddings(self, dto):
        embeddings = dto.get("embeddings")
        return {
            "title_sparse_vector": SparseVector(embeddings["title_embeddings"]["sparse"], V_DIM),
            "title_vector": embeddings["title_embeddings"]["dense"],
            "content_chunks": [
                SupportChunkModel(
                    chunk_content=content_vector["chunk"],
                    chunk_vector=content_vector["dense"],
                    chunk_sparse_vector=SparseVector(content_vector["sparse"], V_DIM),
                ) for content_vector in embeddings["content_embeddings"]
            ]
        } if embeddings else {}

    def dto2orm(self, dto: SupportDTO) -> Optional[SupportModel]:
        info = self.parse_info(dto)
        attachments = self.parse_attachments(dto)
        embeddings = self.parse_embeddings(dto)

        if not info:
            return None

        return SupportModel(**info, **attachments, **embeddings, url=dto["url"])

    def orm2dto(self, orm):
        pass

    async def run_full_crawling_pipeline_async(self, **kwargs):
        with open("config/onestop.json", "r") as f:
            url_dict = json.load(f)

        dtos = []

        for category_key in url_dict.keys():
            sub_categories = url_dict[category_key]
            if isinstance(sub_categories, str):
                _info = {"category": category_key, "title": category_key}
                dtos.append(SupportDTO(info=_info, url=sub_categories))
                continue

            for sub_key in sub_categories.keys():
                sub_category = sub_categories[sub_key]
                if isinstance(sub_category, str):
                    info = SupportDTO(
                        info={
                            "category": category_key,
                            "sub_category": sub_key,
                            "title": sub_key
                        }, url=sub_category
                    )
                    dtos.append(info)
                    continue

                dtos_ = [
                    SupportDTO(info={
                        "category": category_key,
                        "sub_category": sub_key,
                        "title": title
                    }, url=url) for title, url in sub_category.items()
                ]

                dtos += dtos_

        interval = kwargs.get('interval', 30)

        models = []
        try:
            pbar = tqdm(range(0, len(dtos), interval), total=len(dtos))

            for st in pbar:
                ed = min(st + interval, len(dtos))
                pbar.set_postfix({'range': f"{st + 1} ~ {ed}"})
                _dtos = dtos[st:ed]
                supports = await self.support_crawler.scrape_detail_async(_dtos)
                supports = await self.support_embedder.embed_all_async(items=supports, interval=interval)
                support_models = [self.dto2orm(n) for n in supports]
                support_models = [n for n in support_models if n]
                support_models = self.support_repo.create_all(support_models)
                models += support_models

                pbar.update(interval)

                await asyncio.sleep(kwargs.get('delay', 0))

        except TimeoutError as e:
            logger.exception(f"크롤링에 실패하였습니다.")
            logger.exception(e)

        return models

    class SearchOptions(TypedDict):
        count: NotRequired[int]
        lexical_ratio: NotRequired[float]

    def search_supports_with_filter(self, query: str, **opts: Unpack[SearchOptions]):
        from time import time
        st = time()
        embed_result = self.support_embedder._embed_query(query, chunking=False)
        logger.info(f"embed query: {time() - st:.4f}")

        st = time()
        search_results = self.support_repo.search_supports_content_hybrid(
            dense_vector=embed_result["dense"],
            sparse_vector=embed_result["sparse"],
            lexical_ratio=opts.get("lexical_ratio", 0.5),
            k=opts.get("count", 5),
        )
        logger.info(f"hybrid search: {time() - st:.4f}")

        return search_results
