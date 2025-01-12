from abc import abstractmethod
from typing import Generic, List, TypeVar

from aiohttp import ClientSession



DTO = TypeVar("DTO")


class BaseEmbedder(Generic[DTO], metaclass=HTTPMetaclass):
    async def embed_dto_async(
        self, item: DTO, session: Optional[ClientSession] = None
    ) -> DTO:
        if session is None:
            raise ValueError("parameter 'session' cannot be None.")

        return await self._embed_dto_async(item, session=session)

    @abstractmethod
    async def _embed_dto_async(self, item: DTO, session: ClientSession) -> DTO:
        pass

    async def embed_all_async(
        self,
        items: List[DTO],
        interval: int = 30,
        session: Optional[ClientSession] = None,
    ) -> List[DTO]:
        if session is None:
            raise ValueError("parameter 'session' cannot be None.")

        return await self._embed_all_async(items, interval, session=session)

    @abstractmethod
    async def _embed_all_async(
        self, items: List[DTO], interval: int, session: ClientSession
    ) -> List[DTO]:
        pass

