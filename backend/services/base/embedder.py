from abc import ABC, abstractmethod
from typing import Generic, List, Optional

from aiohttp import ClientSession
import requests

from mixins.asyncio import retry_async
from mixins.http_client import HTTPMetaclass
from dotenv import load_dotenv
import os

from services.base.dto import DTO, EmbedResult
from services.base.types.http_client import SessionArgsType

load_dotenv()

EMBED_URL = os.environ.get("EMBED_URL")


class BaseEmbedder(ABC, Generic[DTO], metaclass=HTTPMetaclass):

    async def embed_dtos_async(
        self, items: List[DTO], **kwargs: SessionArgsType
    ) -> List[DTO]:
        session = kwargs.get("session")
        if not session or type(session) is not ClientSession:
            raise ValueError("'session' argument must be provided.")

        return await self._embed_dtos_async(items, **kwargs)

    @abstractmethod
    async def _embed_dtos_async(
        self, items: List[DTO], **kwargs: SessionArgsType
    ) -> List[DTO]:
        pass

    async def embed_dtos_batch_async(
        self,
        items: List[DTO],
        batch_size: int = 30,
        **kwargs: SessionArgsType
    ) -> List[DTO]:
        session = kwargs.get("session")
        if not session or type(session) is not ClientSession:
            raise ValueError("'session' argument must be provided.")

        def parts(_list: List[DTO], n):
            for idx in range(0, len(_list), n):
                yield _list[idx:idx + n]

        parted_items = list(parts(items, batch_size))

        xss = [
            await self.embed_dtos_async(_items, session=session)
            for _items in parted_items
        ]

        return [x for xs in xss for x in xs]

    @retry_async(delay=3)
    async def _embed_async(
        self,
        texts: str | List[str],
        session: ClientSession,
        chunking: bool = True,
        truncate: bool = True,
    ) -> EmbedResult | List[EmbedResult]:
        body = {
            "inputs": texts,
            "chunking": chunking,
            "truncate": truncate
        }
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
        body = {
            "inputs": query,
            "chunking": chunking,
            "truncate": truncate
        }
        res = requests.post(f"{EMBED_URL}/embed", json=body)
        if res.status_code == 200:
            return res.json()

        raise Exception
