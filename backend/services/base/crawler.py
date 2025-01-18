from abc import abstractmethod
import asyncio
from typing import Generic, List, Optional, TypeVar, overload
import re

from aiohttp import ClientSession
import aiohttp
from requests.sessions import HTTPAdapter

from mixins.asyncio import retry_async
from mixins.http_client import HTTPMetaclass
from bs4 import BeautifulSoup
import requests

DTO = TypeVar("DTO")


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
        self, session: Optional[ClientSession] = None, **kwargs
    ) -> List[DTO]:
        if session is None:
            raise ValueError("parameter 'session' cannot be None.")

        return await self._scrape_partial_async(**kwargs, session=session)

    @abstractmethod
    async def _scrape_partial_async(self, session: ClientSession,
                                    **kwargs) -> List[DTO]:
        pass

    @overload
    async def _scrape_async(
        self,
        url: str,
        session: ClientSession,
        retry_delay: float = 5.0
    ) -> BeautifulSoup:
        ...

    @overload
    async def _scrape_async(
        self,
        url: List[str],
        session: ClientSession,
        retry_delay: float = 5.0
    ) -> List[BeautifulSoup]:
        ...

    async def _scrape_async(
        self,
        url: str | List[str],
        session: ClientSession,
        retry_delay: float = 5.0
    ) -> BeautifulSoup | List[BeautifulSoup]:

        @retry_async(delay=retry_delay)
        async def scrape_coroutine(_url):
            async with session.get(_url) as res:
                if res.status == 200:
                    html = await res.read()
                    soup = BeautifulSoup(html, "html5lib")
                    return soup

                raise aiohttp.ClientError

        if isinstance(url, str):
            return await scrape_coroutine(url)
        return await asyncio.gather(*[scrape_coroutine(_url) for _url in url])

    @overload
    def _scrape(self, url: str) -> BeautifulSoup:
        ...

    @overload
    def _scrape(
        self,
        url: List[str],
    ) -> List[BeautifulSoup]:
        ...

    def _scrape(self, url: str | List[str], timeout: int = 180):

        def scrape(_url):
            with requests.Session() as session:
                adapter = HTTPAdapter(max_retries=10)
                session.mount("https://", adapter)
                response = session.get(_url, timeout=timeout)
                if response.status_code == 200:
                    html = response.text
                    soup = BeautifulSoup(html, "html5lib")
                    return soup

            raise Exception

        if isinstance(url, str):
            return scrape(url)

        soups = []
        for _url in url:
            result = scrape(_url)
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
