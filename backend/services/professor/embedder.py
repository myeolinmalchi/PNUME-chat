from typing import List

from services.base import BaseEmbedder
from services.professor.dto import ProfessorDTO
import asyncio


class ProfessorEmbedder(BaseEmbedder[ProfessorDTO]):

    async def _embed_all_async(self, items, interval, session):

        async def embed_partial_async(item):
            from itertools import islice

            inputs: List[str] = []
            lens: List[int] = []

            append = lambda acc, lens, xs: (acc + xs, lens + [len(xs)])
            for k in ["fields", "educations", "careers"]:
                if k in item["additional_info"]:
                    inputs, lens = append(
                        inputs, lens,
                        [f["name"] for f in item["additional_info"][k]]
                    )

            embeddings = await self._embed_async(
                texts=inputs, session=session, chunking=False
            )

            iterator = iter(embeddings)
            embeddings = [list(islice(iterator, length)) for length in lens]

            for e, k in zip(embeddings, ["fields", "educations", "careers"]):
                if k in item["additional_info"]:
                    item["additional_info"][k] = [{
                        **p, "embeddings": e
                    } for p, e in zip(item["additional_info"][k], e)]

            return item

        def parts(_list, n):
            for idx in range(0, len(_list), n):
                yield _list[idx:idx + n]

        parted_professors = list(parts(items, interval))

        professors: List[ProfessorDTO] = []
        for _professors in parted_professors:
            professors += await asyncio.gather(
                *[embed_partial_async(p) for p in _professors]
            )

        return professors
