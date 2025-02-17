import asyncio
from typing import Callable, List, Optional, Tuple, overload, TypeVar, Any
from bs4 import BeautifulSoup
from mixins.asyncio import retry_async
import random

import aiohttp

T = TypeVar("T")


@overload
async def scrape_async(
    url: List[str],
    session: aiohttp.ClientSession,
    post_process: Optional[Callable[[BeautifulSoup], T]] = None,
    retry_delay: float = 5.0,
    delay_range: Tuple[float, float] = (0, 1)
) -> List[T]:
    pass


@overload
async def scrape_async(
    url: str,
    session: aiohttp.ClientSession,
    post_process: Optional[Callable[[BeautifulSoup], T]] = None,
    retry_delay: float = 5.0,
    delay_range: Tuple[float, float] = (0, 1)
) -> T:
    pass


async def scrape_async(
    url: str | List[str],
    session: aiohttp.ClientSession,
    post_process: Optional[Callable[[BeautifulSoup], T]] = None,
    retry_delay: float = 5.0,
    delay_range: Tuple[float, float] = (0, 1)
) -> T | List[T]:

    @retry_async(delay=retry_delay)
    async def help(_url: str) -> Any:
        await asyncio.sleep(random.uniform(*delay_range))
        async with session.get(_url) as res:
            if res.ok:
                html = await res.text(encoding="utf-8", errors="ignore")
                soup = BeautifulSoup(html, "html5lib")
                result = post_process(soup) if post_process else soup
                return result

            raise aiohttp.ClientError

    if isinstance(url, str):
        return await help(url)

    return await asyncio.gather(*[help(url) for url in url])
