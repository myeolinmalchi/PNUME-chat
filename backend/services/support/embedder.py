import asyncio
from typing import List

from services.base import BaseEmbedder
from services.support.dto import SupportDTO


class SupportEmbedder(BaseEmbedder[SupportDTO]):

    async def _embed_all_async(self, items, interval, session):

        def parts(_list, n):
            for idx in range(0, len(_list), n):
                yield _list[idx:idx + n]

        parted_supports = list(parts(items, interval))

        print(items[0])

        supports: List[SupportDTO] = []

        async def embed_partial_async(_supports: List[SupportDTO]):
            _supports = [support for support in _supports if "info" in support]
            _infos = [support["info"] for support in _supports]

            titles_coroutine = self._embed_async(
                texts=[_info["title"] for _info in _infos],
                session=session,
                chunking=False,
            )
            contents_coroutine = self._embed_async(
                texts=[_info["content"] for _info in _infos],
                session=session,
                chunking=True,
            )

            embeddings = await asyncio.gather(titles_coroutine, contents_coroutine)

            return [
                SupportDTO(
                    **support,
                    **{"embeddings": {
                        "title_embeddings": title_vector,
                        "content_embeddings": content_vector,
                    }}
                ) for support, title_vector, content_vector in zip(_supports, embeddings[0], embeddings[1])
            ]

        for _supports in parted_supports:
            supports += await embed_partial_async(_supports)

        return supports
