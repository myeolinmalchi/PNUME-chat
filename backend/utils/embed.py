from typing import Dict, List, Literal, Optional, overload

from aiohttp import ClientSession
from dotenv import load_dotenv
import requests
import os

from utils.semaphore import http_semaphore

load_dotenv()

embed_url = os.environ.get("EMBED_URL")


class EmbedResult(Dict):
    chunk: Optional[str] = None
    dense: List[float]
    sparse: Dict[int, float]


EmbedResponse = List[List[EmbedResult]] | List[EmbedResult] | EmbedResult


@overload
def embed_onnx(texts: str, chunking: Literal[False], truncate: bool) -> EmbedResult: ...


@overload
def embed_onnx(
    texts: List[str], chunking: Literal[False], truncate: bool
) -> EmbedResult: ...


@overload
def embed_onnx(
    texts: str, chunking: Literal[True], truncate: bool
) -> List[EmbedResult]: ...


@overload
def embed_onnx(
    texts: List[str], chunking: Literal[True], truncate: bool
) -> List[List[EmbedResult]]: ...


def embed_onnx(
    texts: str | List[str],
    chunking: bool = True,
    truncate: bool = True,
) -> EmbedResponse:
    body = {"inputs": texts, "chunking": chunking, "truncate": truncate}
    res = requests.post(f"{embed_url}/embed", json=body)
    if res.status_code == 200:
        data = res.json()
        return data

    raise Exception("텍스트 임베딩에 실패했습니다.")


@overload
async def aembed_onnx(
    texts: List[str],
    session: ClientSession,
    chunking: Literal[True] = True,
    truncate: bool = True,
) -> List[List[EmbedResult]]: ...


@overload
async def aembed_onnx(
    texts: List[str],
    session: ClientSession,
    chunking: Literal[False] = False,
    truncate: bool = True,
) -> List[EmbedResult]: ...


@overload
async def aembed_onnx(
    texts: List[str],
    session: ClientSession,
    chunking: Literal[False] = False,
    truncate: bool = True,
) -> List[EmbedResult]: ...


@overload
async def aembed_onnx(
    texts: str,
    session: ClientSession,
    chunking: Literal[True] = True,
    truncate: bool = True,
) -> List[EmbedResult]: ...


@overload
async def aembed_onnx(
    texts: str,
    session: ClientSession,
    chunking: Literal[False] = False,
    truncate: bool = True,
) -> EmbedResult: ...


@http_semaphore()
async def aembed_onnx(
    texts: str | List[str],
    session: ClientSession,
    chunking: bool = True,
    truncate: bool = True,
) -> EmbedResponse:
    body = {"inputs": texts, "chunking": chunking, "truncate": truncate}
    async with session.post(f"{embed_url}/embed", json=body) as res:
        if res.status == 200:
            data = await res.json()
            return data

        raise Exception("텍스트 임베딩에 실패했습니다.")
