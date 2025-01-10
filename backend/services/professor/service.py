from pgvector.sqlalchemy import SparseVector
from db.common import V_DIM
from db.models.professor import ProfessorModel, PROFESSOR_MODEL_MAP
from db.repositories.base import transaction
from db.repositories.professor import ProfessorRepository
from services.professor import ProfessorDTO, ProfessorEmbedder, ProfessorCrawler


class ProfessorService:

    def __init__(
        self,
        professor_repo: ProfessorRepository,
        professor_embedder: ProfessorEmbedder,
        professor_crawler: ProfessorCrawler,
    ):
        self.professor_repo = professor_repo
        self.professor_crawler = professor_crawler
        self.professor_embedder = professor_embedder

    def dto2orm(self, dto: ProfessorDTO):
        _professor = {**dto["basic_info"]}

        def dict2dict(_dict: dict):
            return {
                **({
                    k: v
                    for k, v in _dict.items() if k is not "seq"
                }),
                **({
                    "dense_vector": _dict["embeddings"]["dense"],
                    "sparse_vector": SparseVector(_dict["embeddings"]["sparse"], V_DIM)
                } if "embeddings" in _dict else {})
            }

        for key in dto["additional_info"].keys():
            Model = PROFESSOR_MODEL_MAP[key]
            _infos = [dict2dict(info) for info in dto["additional_info"][key]]
            _professor[key] = [Model(**info) for info in _infos]

        return ProfessorModel(**_professor)

    @transaction()
    async def run_full_crawling_pipeline_async(self):
        professors = await self.professor_crawler.scrape_all_async(10)
        professors = await self.professor_embedder.aembed_batch(professors)
        professors = [self.dto2orm(p) for p in professors]
        professors = self.professor_repo.create_all(professors)

        return professors
