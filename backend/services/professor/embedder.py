from itertools import cycle
from typing import List

from services.base import BaseEmbedder
from services.professor import ProfessorDTO


class ProfessorEmbedder(BaseEmbedder[ProfessorDTO]):

    async def _embed_all_async(self, items, interval, session):

        async def embed_partial_async(_professors: List[ProfessorDTO]):
            _infos = [professor["info"] for professor in _professors]
            _details = [info["detail"] for info in _infos if "detail" in info]

            details, indicies = [], []
            for idx, p in enumerate(_professors):
                _info = p["info"]
                if "detail" in _info:
                    details.append(_info["detail"])
                    indicies.append(idx)

            embeddings = await self._embed_async(
                texts=_details, session=session, chunking=True
            )

            assert isinstance(embeddings, list)
            _embeddings = cycle(embeddings)

            return [
                ProfessorDTO(
                    **professor,
                    **({
                        "embeddings": next(_embeddings)
                    } if idx in indicies else {})
                ) for idx, professor in enumerate(_professors)
            ]

        def parts(_list, n):
            for idx in range(0, len(_list), n):
                yield _list[idx:idx + n]

        parted_professors = list(parts(items, interval))

        professors: List[ProfessorDTO] = []
        for _professors in parted_professors:
            professors += await embed_partial_async(_professors)

        return professors
