from pgvector.sqlalchemy import SparseVector
from db.common import V_DIM
from db.models.support import SupportAttachmentModel, SupportChunkModel, SupportModel
from db.repositories.base import transaction
from db.repositories.support import SupportRepository
from services.base.embedder import embed
from services.base.service import BaseDomainService
from typing import Optional, TypedDict, NotRequired, Unpack

from services.support.crawler import SupportCrawler
from services.support.dto import SupportDTO
import logging

from services.support.embedder import SupportEmbedder

logger = logging.getLogger(__name__)


class SupportService(BaseDomainService[SupportDTO, SupportModel]):

    def __init__(
        self, support_repo: SupportRepository, support_crawler: SupportCrawler, support_embedder: SupportEmbedder
    ):
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
        attachments = [{"name": att.name, "url": att.url} for att in orm.attachments]
        info = {"title": orm.title, "sub_category": orm.sub_category, "category": orm.category, "content": orm.content}
        return SupportDTO(**{"info": info, "attachments": attachments, "url": orm.url})

    def dto2context(self, dto: SupportDTO) -> str:
        info = dto["info"]

        return f"""
        <support>
            <title>{info["title"]}</title>
            <metadata>
                <url>{dto["url"]}</url>
                <category>{info["category"]}</category>
                <sub_category>{info["sub_category"]}</sub_category>
                <title>{info["title"]}</title>
            </metadata>
            <content>
                {info["content"]}
            </content>
        </support>
        """

    class SearchOptions(TypedDict):
        count: NotRequired[int]
        lexical_ratio: NotRequired[float]

    @transaction()
    def search_supports_with_filter(self, query: str, **opts: Unpack[SearchOptions]):
        from time import time
        st = time()
        embed_result = embed(query, chunking=False)
        logger.info(f"embed query: {time() - st:.4f}")

        st = time()
        search_results = self.support_repo.search_supports_hybrid(
            dense_vector=embed_result["dense"],
            sparse_vector=embed_result["sparse"],
            lexical_ratio=opts.get("lexical_ratio", 0.5),
            k=opts.get("count", 5),
        )
        logger.info(f"hybrid search: {time() - st:.4f}")

        return [self.orm2dto(orm) for orm in search_results]
