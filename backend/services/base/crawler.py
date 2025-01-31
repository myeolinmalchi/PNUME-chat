from abc import abstractmethod
import asyncio
from typing import Callable, Generic, List, Optional, TypeVar, TypedDict, overload
import re

from aiohttp import ClientSession
import aiohttp

from mixins.asyncio import retry_async, retry_sync
from mixins.http_client import HTTPMetaclass
from bs4 import BeautifulSoup
import requests

DTO = TypeVar("DTO")


class BaseCrawler(Generic[DTO], metaclass=HTTPMetaclass):

    async def scrape_detail_async(self,
                                  dtos: List[DTO],
                                  session: Optional[ClientSession] = None,
                                  **kwargs) -> List[DTO]:
        if session is None:
            raise ValueError("parameter 'session' cannot be None.")

        return await self._scrape_detail_async(dtos, session, **kwargs)

    async def _scrape_detail_async(self, dtos: List[DTO], session: ClientSession, **kwargs) -> List[DTO]:
        urls = [dto["url"] for dto in dtos]
        soups = await self._scrape_async(urls, session=session)

        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(None, self._parse_detail, dto, soup) for soup, dto in zip(soups, dtos)]

        dtos_ = await asyncio.gather(*tasks)
        dtos_ = [dto for dto in dtos_ if dto]

        return dtos_

    @abstractmethod
    def _parse_detail(self, dto: DTO, soup: BeautifulSoup) -> Optional[DTO]:
        pass

    @overload
    async def _scrape_async(self, url: str, session: ClientSession, retry_delay: float = 5.0) -> BeautifulSoup:
        ...

    @overload
    async def _scrape_async(self,
                            url: List[str],
                            session: ClientSession,
                            retry_delay: float = 5.0) -> List[BeautifulSoup]:
        ...

    async def _scrape_async(self,
                            url: str | List[str],
                            session: ClientSession,
                            retry_delay: float = 5.0) -> BeautifulSoup | List[BeautifulSoup]:

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
    def _scrape(self, url: str, timeout: int = 600, is_success=lambda _: True) -> BeautifulSoup:
        ...

    @overload
    def _scrape(self, url: List[str], timeout: int = 600, is_success=lambda _: True) -> List[BeautifulSoup]:
        ...

    def _scrape(
        self, url: str | List[str], timeout: int = 600, is_success: Callable[[BeautifulSoup], bool] = lambda _: True
    ):

        @retry_sync(is_success=is_success)
        def scrape(_url):
            response = requests.get(_url, timeout=timeout)
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, "html5lib")
                return soup

            raise requests.ConnectionError()

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
