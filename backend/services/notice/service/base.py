from abc import abstractmethod
import logging
from typing import List, NotRequired, Optional, Required, TypedDict, Unpack
from pgvector.sqlalchemy import SparseVector

from db.common import V_DIM
from db.models import AttachmentModel, NoticeChunkModel, NoticeModel
from db.models.calendar import SemesterModel
from db.models.university import DepartmentModel
from db.repositories import NoticeRepository

from db.repositories.base import transaction
from db.repositories.calendar import SemesterRepository
from db.repositories.university import UniversityRepository
from services.base import BaseService

from services.base.types.calendar import DateRangeType, SemesterType
from services.notice.dto import NoticeDTO
from services.notice.embedder import NoticeEmbedder
from services.notice.crawler.base import NoticeCrawlerBase

logger = logging.getLogger(__name__)


class SearchOptions(TypedDict, total=False):
    count: NotRequired[int]
    lexical_ratio: NotRequired[float]
    semesters: Required[List[SemesterType]]
    departments: Required[List[str]]


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

    def _parse_info(self, dto):
        info = dto.get("info")
        return info if info else {}

    def _parse_attachments(self, dto):
        attachments = dto.get("attachments")
        return {
            "attachments": [AttachmentModel(**att) for att in attachments]
        } if attachments else {}

    def _parse_embeddings(self, dto):
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

    def dto2orm(self, dto: NoticeDTO) -> Optional[NoticeModel]:
        info = self._parse_info(dto)
        attachments = self._parse_attachments(dto)
        embeddings = self._parse_embeddings(dto)

        if not info:
            return None

        department_model = self.university_repo.find_department_by_name(
            info["department"]
        )
        assert type(department_model) is DepartmentModel
        del info["department"]

        return NoticeModel(
            **info,
            **attachments,
            **embeddings,
            url=dto["url"],
            department_id=department_model.id
        )

    def orm2dto(self, orm: NoticeModel) -> NoticeDTO:
        ...

    @abstractmethod
    async def run_full_crawling_pipeline_async(self,
                                               **kwargs) -> List[NoticeModel]:
        pass

    @transaction()
    def search_notices_with_filter(
        self, query: str, **opts: Unpack[SearchOptions]
    ):
        embed_result = self.notice_embedder._embed_query(query, chunking=False)

        semesters = opts['semesters']
        departments = opts['departments']

        if not self.semester_repo:
            raise ValueError("'NoticeService.semester_repo' must be provided")

        semester_ids = []

        semester_models = self.semester_repo.search_semesters(semesters)
        if not semester_models:
            raise ValueError(f"학기 정보를 찾을 수 없습니다: {semesters}")

        assert isinstance(semester_models, list)
        semester_ids = [s.id for s in semester_models]

        search_results = self.notice_repo.search_notices_hybrid(
            dense_vector=embed_result["dense"],
            sparse_vector=embed_result["sparse"],
            lexical_ratio=opts.get("lexical_ratio", 0.5),
            semester_ids=semester_ids,
            departments=departments,
            k=opts.get("count", 5),
        )

        return search_results

    @transaction()
    def add_semester_info(self, semester: SemesterType, batch_size: int = 500):

        if not self.semester_repo:
            raise ValueError("'semester_repo' not provided")

        semester_model = self.semester_repo.search_semesters(semester)

        if not semester_model:
            raise ValueError(f"semester info not exists: {semester}")

        assert type(semester_model) is SemesterModel

        st, ed = semester_model.st_date, semester_model.ed_date
        date_range = DateRangeType(st_date=st, ed_date=ed)
        total_records = self.notice_repo.search_total_records(
            date_ranges=[date_range]
        )

        done = []

        from tqdm import tqdm
        pbar = tqdm(
            range(0, total_records, batch_size),
            desc=f"학기 정보 추가({semester['year']}-{semester['type_']})"
        )
        for offset in pbar:
            notices = self.notice_repo.update_semester(
                semester_model, batch_size, offset
            )
            done += notices

        return done
