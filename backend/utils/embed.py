from typing import Dict, List, Literal, Optional, overload
from asyncio.locks import Semaphore

from aiohttp import ClientSession
from dotenv import load_dotenv
import requests
import os

load_dotenv()

embed_url = os.environ.get("EMBED_URL")


class EmbedResult(Dict):
    chunk: Optional[str] = None
    dense: List[float]
    sparse: Dict[int, float]


EmbedResponse = List[List[EmbedResult]] | List[EmbedResult] | EmbedResult


def embed_onnx(
    texts: List[str],
) -> Optional[EmbedResponse]:
    body = {
        "inputs": texts,
    }
    res = requests.post(f"{embed_url}/embed", json=body)
    if res.status_code == 200:
        data = res.json()
        return data


@overload
async def aembed_onnx(
    session: ClientSession,
    semaphore: Semaphore,
    texts: List[str],
    chunking: Literal[True],
    truncate: bool = True,
) -> Optional[List[List[EmbedResult]]]: ...


@overload
async def aembed_onnx(
    session: ClientSession,
    semaphore: Semaphore,
    texts: List[str],
    chunking: Literal[False],
    truncate: bool = True,
) -> Optional[List[EmbedResult]]: ...


@overload
async def aembed_onnx(
    session: ClientSession,
    semaphore: Semaphore,
    texts: List[str],
    chunking: Literal[False],
    truncate: bool = True,
) -> Optional[List[EmbedResult]]: ...


@overload
async def aembed_onnx(
    session: ClientSession,
    semaphore: Semaphore,
    texts: str,
    chunking: Literal[True],
    truncate: bool = True,
) -> Optional[List[EmbedResult]]: ...


@overload
async def aembed_onnx(
    session: ClientSession,
    semaphore: Semaphore,
    texts: str,
    chunking: Literal[False],
    truncate: bool = True,
) -> Optional[EmbedResult]: ...


async def aembed_onnx(
    session: ClientSession,
    semaphore: Semaphore,
    texts: str | List[str],
    chunking: bool = True,
    truncate: bool = True,
) -> Optional[EmbedResponse]:
    async with semaphore:
        body = {"inputs": texts, "chunking": chunking, "truncate": truncate}
        async with session.post(f"{embed_url}/embed", json=body) as res:
            if res.status == 200:
                data = await res.json()
                return data
            from pprint import pprint

            pprint(f"status code: {res.status}")
            pprint(await res.json())
