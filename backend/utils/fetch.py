from asyncio import Semaphore
import asyncio
import aiohttp

from typing import List, Optional, Unpack
from aiohttp import ClientSession
from aiohttp.client import _RequestOptions


class _AFetchOptions(_RequestOptions):
    url: str
    method: str


async def afetch(
    session: ClientSession, semaphore: Semaphore, **kwargs: Unpack[_AFetchOptions]
):
    try:
        async with semaphore:
            async with session.request(**kwargs) as res:
                return await res.read()
    except Exception as e:
        print(e)


async def afetch_all(
    options: List[_AFetchOptions], limit: int = 5
) -> List[Optional[bytes]]:
    semaphore = asyncio.Semaphore(limit)
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(
            *[afetch(session, semaphore, **option) for option in options]
        )
