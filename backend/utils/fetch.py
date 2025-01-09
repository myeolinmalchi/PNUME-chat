import asyncio
import aiohttp

from typing import List, Optional, Unpack
from aiohttp import ClientSession
from aiohttp.client import _RequestOptions

from utils.semaphore import http_semaphore


class _AFetchOptions(_RequestOptions):
    url: str
    method: str


@http_semaphore()
async def afetch(session: ClientSession, **kwargs: Unpack[_AFetchOptions]):
    async with session.request(**kwargs) as res:
        return await res.read()


async def afetch_all(options: List[_AFetchOptions]) -> List[Optional[bytes]]:
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(*[afetch(session, **option) for option in options])
