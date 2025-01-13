from typing import Optional
from pgvector.sqlalchemy import SparseVector

from db.common import V_DIM
from db.models import ProfessorModel, PROFESSOR_MODEL_MAP
from db.repositories import transaction, ProfessorRepository

from services.base import BaseService
from services.professor import ProfessorDTO, ProfessorMEEmbedder, ProfessorMECrawler


class ProfessorMEService(BaseService[ProfessorDTO, ProfessorModel]):

    def __init__(
        self,
        professor_repo: ProfessorRepository,
        professor_embedder: ProfessorMEEmbedder,
        professor_crawler: ProfessorMECrawler,
    ):
        self.professor_repo = professor_repo
        self.professor_crawler = professor_crawler
        self.professor_embedder = professor_embedder

    def dto2orm(self, dto: ProfessorDTO):
        _professor = {**dto["basic_info"]}

        major_minor = self.professor_repo.find_major_minor(
            _professor["major"], _professor["minor"]
        )

        del _professor["major"]
        del _professor["minor"]

        _professor = {**_professor, **major_minor}

        def dict2dict(_dict: dict):
            return {
                **({
                    k: v
                    for k, v in _dict.items() if k != "seq" and k != "embeddings"
                }),
                **({
                    "dense_vector": _dict["embeddings"]["dense"],
                    "sparse_vector": SparseVector(
                        _dict["embeddings"]["sparse"], V_DIM
                    )
                } if "embeddings" in _dict else {})
            }

        for key in dto["additional_info"].keys():
            Model = PROFESSOR_MODEL_MAP[key]
            _infos = [dict2dict(info) for info in dto["additional_info"][key]]
            _professor[key] = [Model(**info) for info in _infos]

        return ProfessorModel(**_professor, seq=dto["seq"])

    def orm2dto(self, orm) -> ProfessorDTO:
        ...

    @transaction()
    async def run_full_crawling_pipeline_async(self, **kwargs):
        professors = await self.professor_crawler.scrape_all_async(
            interval=kwargs.get('interval', 10), delay=kwargs.get('delay', 0)
        )
        professors = await self.professor_embedder.embed_all_async(professors)
        professors = [self.dto2orm(p) for p in professors]
        professors = self.professor_repo.create_all(professors)

        return professors


def create_professor_me_service(
    professor_repo: Optional[ProfessorRepository] = None,
    professor_crawler: Optional[ProfessorMECrawler] = None,
    professor_embedder: Optional[ProfessorMEEmbedder] = None
):
    professor_repo = ProfessorRepository(
    ) if not professor_repo else professor_repo
    professor_crawler = ProfessorMECrawler(
    ) if not professor_crawler else professor_crawler
    professor_embedder = ProfessorMEEmbedder(
    ) if not professor_embedder else professor_embedder

    professor_service = ProfessorMEService(
        professor_repo, professor_embedder, professor_crawler
    )

    return professor_service
