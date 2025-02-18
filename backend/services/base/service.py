from abc import abstractmethod, ABC
from typing import Generic, List, NotRequired, Optional, TypeVar, TypedDict

from db.common import Base
from mixins.http_client import HTTPMetaclass
from services.base.dto import DTO

ORM = TypeVar("ORM", bound=Base)


class CrawlingParams(TypedDict):
    delay: NotRequired[float]
    interval: NotRequired[int]

    with_embeddings: NotRequired[bool]


class BaseService(ABC):
    pass


class BaseDomainService(Generic[DTO, ORM], BaseService):

    @abstractmethod
    def dto2orm(self, dto: DTO) -> Optional[ORM]:
        pass

    @abstractmethod
    def orm2dto(self, orm: ORM) -> Optional[DTO]:
        pass


class BaseCrawlerService(BaseDomainService[DTO, ORM], metaclass=HTTPMetaclass):

    @abstractmethod
    async def run_crawling_pipeline(self, **kwargs) -> List[DTO]:
        pass
