from abc import abstractmethod
from typing import Dict, Generic, List, NotRequired, Optional, TypeVar, TypedDict

from aiohttp import ClientSession
import requests

from mixins.asyncio import retry_async
from mixins.http_client import HTTPMetaclass
from dotenv import load_dotenv
import os

load_dotenv()

EMBED_URL = os.environ.get("EMBED_URL")


class EmbedResult(TypedDict):
    chunk: NotRequired[str]
    dense: List[float]
    sparse: Dict[int, float]


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

    @retry_async(delay=3)
    async def _embed_async(
        self,
        texts: str | List[str],
        session: ClientSession,
        chunking: bool = True,
        truncate: bool = True,
    ) -> EmbedResult | List[EmbedResult]:
        body = {"inputs": texts, "chunking": chunking, "truncate": truncate}
        async with session.post(f"{EMBED_URL}/embed", json=body) as res:
            if res.status == 200:
                data = await res.json()
                return data

            raise Exception("텍스트 임베딩에 실패했습니다.")

    def _embed_query(
        self,
        query: str | List[str],
        chunking: bool = True,
        truncate: bool = True
    ):
        body = {"inputs": query, "chunking": chunking, "truncate": truncate}
        res = requests.post(f"{EMBED_URL}/embed", json=body)
        if res.status_code == 200:
            return res.json()

        raise Exception
