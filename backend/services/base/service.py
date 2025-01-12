from abc import abstractmethod, ABC
from typing import Generic, List, NotRequired, TypeVar, TypedDict

DTO = TypeVar("DTO")
ORM = TypeVar("ORM")


class CrawlingParams(TypedDict):
    delay: NotRequired[float]
    interval: NotRequired[int]

    with_embeddings: NotRequired[bool]


class BaseService(Generic[DTO, ORM], ABC):

    @abstractmethod
    def dto2orm(self, dto: DTO) -> ORM:
        pass

    @abstractmethod
    def orm2dto(self, orm: ORM) -> DTO:
        pass

    @abstractmethod
    async def run_full_crawling_pipeline_async(self, **kwargs) -> List[ORM]:
        pass
