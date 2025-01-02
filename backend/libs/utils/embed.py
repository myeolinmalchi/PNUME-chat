from typing import List, Optional
from asyncio.locks import Semaphore

from aiohttp import ClientSession
from dotenv import load_dotenv
import requests
import os

load_dotenv()

tei_host = os.environ.get("TEI_HOST")
tei_port = os.environ.get("TEI_PORT")


def embed_tei(
    texts: List[str],
    normalize: Optional[bool] = None,
    truncate: bool = True,
    # truncation_direction: Literal["left", "right"] = "right",
    embed_sparse: bool = False,
) -> Optional[List[float]]:
    if normalize is None:
        normalize = not embed_sparse

    body = {
        "inputs": texts,
        "normalize": normalize,
        "truncate": truncate,
        # "truncation_direction": truncation_direction,
    }

    path = "embed_sparse" if embed_sparse else "embed"
    res = requests.post(f"{tei_host}:{tei_port}/{path}", json=body)

    if res.status_code == 200:
        data = res.json()
        return data


async def aembed_tei(
    session: ClientSession,
    semaphore: Semaphore,
    texts: List[str],
    normalize: Optional[bool] = None,
    truncate: bool = True,
    embed_sparse: bool = False,
) -> Optional[List[float]]:
    async with semaphore:
        if normalize is None:
            normalize = not embed_sparse

        body = {
            "inputs": texts,
            "normalize": normalize,
            "truncate": truncate,
        }

        path = "embed_sparse" if embed_sparse else "embed"
        async with session.post(f"{tei_host}:{tei_port}/{path}", json=body) as res:
            if res.status == 200:
                data = await res.json()
                return data
