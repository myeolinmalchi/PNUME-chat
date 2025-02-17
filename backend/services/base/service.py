from abc import abstractmethod, ABC
from typing import Generic, List, NotRequired, TypeVar, TypedDict

DTO = TypeVar("DTO")
ORM = TypeVar("ORM")


class CrawlingParams(TypedDict):
    delay: NotRequired[float]
    interval: NotRequired[int]

    with_embeddings: NotRequired[bool]


class BaseService(Generic[DTO, ORM]):

    def dto2orm(self, dto: DTO) -> ORM:
        raise NotImplementedError()

    def orm2dto(self, orm: ORM) -> DTO:
        raise NotImplementedError()

        raise NotImplementedError()
    async def run_crawling_pipeline(self, **kwargs) -> List[DTO]:
