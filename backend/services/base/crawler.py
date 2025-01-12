from abc import abstractmethod
import asyncio
from typing import Generic, List, Optional, TypeVar, overload
import re

from aiohttp import ClientSession
import aiohttp

from mixins.asyncio import retry_async
from mixins.http_client import HTTPMetaclass
from bs4 import BeautifulSoup
import requests

DTO = TypeVar("DTO")

domain = "https://me.pusan.ac.kr"


class BaseCrawler(Generic[DTO], metaclass=HTTPMetaclass):

    async def scrape_all_async(
        self,
        interval: int,
        delay: float = 0,
        session: Optional[ClientSession] = None,
        **kwargs
    ) -> List[DTO]:
        if session is None:
            raise ValueError("parameter 'session' cannot be None.")

        return await self._scrape_all_async(
            interval, delay, **kwargs, session=session
        )

    @abstractmethod
    async def _scrape_all_async(
        self, interval: int, delay: float, session: ClientSession, **kwargs
    ) -> List[DTO]:
        pass

    async def scrape_partial_async(
        self,
        seqs: List[int],
        session: Optional[ClientSession] = None,
        **kwargs
    ) -> List[DTO]:
        if session is None:
            raise ValueError("parameter 'session' cannot be None.")

        return await self._scrape_partial_async(seqs, **kwargs, session=session)

    @abstractmethod
    async def _scrape_partial_async(
        self, seqs: List[int], session: ClientSession, **kwargs
    ) -> List[DTO]:
        pass

    @overload
    async def _scrape_async(
        self, path: str, session: ClientSession
    ) -> BeautifulSoup:
        ...

    @overload
    async def _scrape_async(self, path: List[str],
                            session: ClientSession) -> List[BeautifulSoup]:
        ...

    async def _scrape_async(
        self, path: str | List[str], session: ClientSession
    ) -> BeautifulSoup | List[BeautifulSoup]:

        @retry_async(delay=5)
        async def scrape_coroutine(_path):
            test = len(_path) == 0 or _path.startswith("/")
            _path = _path if test else f"/{_path}"
            async with session.get(f"{domain}{_path}") as res:
                if res.status == 200:
                    html = await res.read()
                    soup = BeautifulSoup(html, "html.parser")
                    return soup

                raise aiohttp.ClientError

        if isinstance(path, str):
            return await scrape_coroutine(path)
        return await asyncio.gather(
            *[scrape_coroutine(_path) for _path in path]
        )

    @overload
    def _scrape(self, path: str) -> BeautifulSoup:
        ...

    @overload
    def _scrape(
        self,
        path: List[str],
    ) -> List[BeautifulSoup]:
        ...

    def _scrape(self, path: str | List[str]):

        def scrape(_path):
            test = len(path) == 0 or _path.startswith("/")
            _path = _path if test else f"/{_path}"

            response = requests.get(f"{domain}{_path}", timeout=3.0)
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, "html.parser")
                return soup

            raise Exception

        if isinstance(path, str):
            return scrape(path)

        soups = []
        for _path in path:
            result = scrape(_path)
            soups.append(result)

        return soups

    def _preprocess_text(self, text: str, remove_newline: bool = False):
        """텍스트 전처리"""
        text = re.sub(r"\\+", "", text)   # 백슬래시(\\) 제거
        text = re.sub(r"\n+", "\n", text) # 여러 줄바꿈을 하나의 공백으로 대체
        text = re.sub(r"\t", "", text)    # 여러 줄바꿈을 하나의 공백으로 대체
        text = re.sub(r"\r", "", text)    # 여러 줄바꿈을 하나의 공백으로 대체
        exclude_base64 = re.compile(r"data:image/[a-zA-Z]+;base64,[^\"']+")
        text = re.sub(exclude_base64, "", text)
        if remove_newline:
            text = re.sub(r"\n", "", text)
        re.sub(r"\s+", " ", text).strip()
        return text
