import asyncio
from typing import List

from aiohttp import ClientSession, ClientTimeout
from services.base import BaseEmbedder
from services.professor.dto import ProfessorDTO
from utils.embed import aembed_onnx


class ProfessorEmbedder(BaseEmbedder[ProfessorDTO]):
    async def aembed(self, item, sess):
        from itertools import islice

        inputs: List[str] = []
        lens: List[int] = []

        append = lambda acc, lens, xs: (acc + xs, lens + [len(xs)])
        for k in ["fields", "educations", "careers"]:
            if k in item:
                inputs, lens = append(inputs, lens, [f["name"] for f in item[k]])

        embeddings = await aembed_onnx(texts=inputs, session=sess, chunking=False)

        iterator = iter(embeddings)
        embeddings = [list(islice(iterator, length)) for length in lens]

        for e, k in zip(embeddings, ["fields", "educations", "careers"]):
            if k in item:
                item[k] = [{**p, "embeddings": e} for p, e in zip(item[k], e)]

        return item

    async def aembed_batch(self, items, timeout=60):
        timeout = ClientTimeout(total=timeout)
        async with ClientSession(timeout=timeout) as sess:
            coroutines = [self.aembed(p, sess) for p in items]
            professors = await asyncio.gather(*coroutines)

        return professors
