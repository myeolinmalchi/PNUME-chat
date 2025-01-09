import asyncio
from typing import List, Optional
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
from aiohttp import ClientSession
import aiohttp

import requests
from bs4 import BeautifulSoup

from utils.semaphore import http_semaphore

domain = "https://me.pusan.ac.kr"


def scrape(path: str) -> Optional[BeautifulSoup]:
    try:
        test = len(path) == 0 or path.startswith("/")
        _path = path if test else f"/{path}"

        response = requests.get(f"{domain}{_path}", timeout=3.0)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            return soup

    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
        return


@http_semaphore()
async def ascrape(session: ClientSession, path: str) -> Optional[BeautifulSoup]:
    test = len(path) == 0 or path.startswith("/")
    _path = path if test else f"/{path}"
    async with session.get(f"{domain}{_path}") as res:
        if res.status == 200:
            html = await res.read()
            soup = BeautifulSoup(html, "html.parser")
            return soup


async def ascrape_all(
    paths: List[str], timeout: int = 60
) -> List[Optional[BeautifulSoup]]:
    client_timeout = aiohttp.ClientTimeout(timeout)
    async with aiohttp.ClientSession(timeout=client_timeout) as session:
        return await asyncio.gather(*[ascrape(session, path) for path in paths])
