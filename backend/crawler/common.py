import asyncio
from asyncio.locks import Semaphore
from typing import List, Optional
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
from aiohttp import ClientSession
import aiohttp

import requests

domain = "https://me.pusan.ac.kr"

from bs4 import BeautifulSoup


def fetch(path: str) -> Optional[BeautifulSoup]:
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


async def afetch(
    session: ClientSession, path: str, semaphore: Semaphore
) -> Optional[BeautifulSoup]:
    test = len(path) == 0 or path.startswith("/")
    _path = path if test else f"/{path}"
    try:
        async with semaphore:
            async with session.get(f"{domain}{_path}") as res:
                if res.status == 200:
                    # html = await res.text(encoding="utf-8")
                    html = await res.read()
                    soup = BeautifulSoup(html, "html.parser")
                    return soup
    except Exception as e:
        print(e)


async def afetch_all(paths: List[str], limit: int = 5) -> List[Optional[BeautifulSoup]]:
    semaphore = asyncio.Semaphore(limit)
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(
            *[afetch(session, path, semaphore) for path in paths]
        )
