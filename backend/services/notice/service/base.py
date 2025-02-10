from abc import abstractmethod
import logging
from typing import List, NotRequired, Optional, TypedDict, Unpack
from pgvector.sqlalchemy import SparseVector

from db.common import V_DIM
from db.models import AttachmentModel, NoticeChunkModel, NoticeModel
from db.repositories import NoticeRepository

from db.repositories.university import UniversityRepository
from services.base import BaseService

from services.notice.dto import NoticeDTO
from services.notice.embedder import NoticeEmbedder
from services.notice.crawler.base import NoticeCrawlerBase

logger = logging.getLogger(__name__)


class NoticeServiceBase(BaseService):

    def __init__(
        self,
        notice_repo: NoticeRepository,
        notice_embedder: NoticeEmbedder,
        notice_crawler: NoticeCrawlerBase,
        university_repo: UniversityRepository,
        semester_repo: Optional[SemesterRepository] = None
    ):
        self.notice_repo = notice_repo
        self.notice_embedder = notice_embedder
        self.notice_crawler = notice_crawler
        self.university_repo = university_repo
        self.semester_repo = semester_repo

    def parse_info(self, dto):
        info = dto.get("info")
        return info if info else {}

    def parse_attachments(self, dto):
        attachments = dto.get("attachments")
        return {"attachments": [AttachmentModel(**att) for att in attachments]} if attachments else {}

    def parse_embeddings(self, dto):
        embeddings = dto.get("embeddings")
        return {
            "title_sparse_vector": SparseVector(embeddings["title_embeddings"]["sparse"], V_DIM),
            "title_vector": embeddings["title_embeddings"]["dense"],
            "content_chunks": [
                NoticeChunkModel(
                    chunk_content=content_vector["chunk"],
                    chunk_vector=content_vector["dense"],
                    chunk_sparse_vector=SparseVector(content_vector["sparse"], V_DIM),
                ) for content_vector in embeddings["content_embeddings"]
            ]
        } if embeddings else {}

    def dto2orm(self, dto: NoticeDTO) -> Optional[NoticeModel]:
        info = self.parse_info(dto)
        attachments = self.parse_attachments(dto)
        embeddings = self.parse_embeddings(dto)

        if not info:
            return None

        dep_id = self.university_repo.find_department_by_name(info["department"])
        del info["department"]

        return NoticeModel(**info, **attachments, **embeddings, url=dto["url"], department_id=dep_id.id)

    def orm2dto(self, orm: NoticeModel) -> NoticeDTO:
        ...

    @abstractmethod
    async def run_full_crawling_pipeline_async(self, **kwargs) -> List[NoticeModel]:
        pass

    class SearchOptions(TypedDict):
        count: NotRequired[int]
        lexical_ratio: NotRequired[float]

    def search_notices_with_filter(self, query: str, **opts: Unpack[SearchOptions]):
        from time import time
        st = time()
        embed_result = self.notice_embedder._embed_query(query, chunking=False)
        logger.info(f"embed query: {time() - st:.4f}")

        st = time()
        search_results = self.notice_repo.search_notices_hybrid(
            dense_vector=embed_result["dense"],
            sparse_vector=embed_result["sparse"],
            lexical_ratio=opts.get("lexical_ratio", 0.5),
            k=opts.get("count", 5),
            year=2024,
            departments=["정보컴퓨터공학부"]
        )
        logger.info(f"hybrid search: {time() - st:.4f}")

        return search_results
