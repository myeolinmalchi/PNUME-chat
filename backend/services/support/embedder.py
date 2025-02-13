import asyncio

from services.base import BaseEmbedder
from services.support.dto import SupportDTO


class SupportEmbedder(BaseEmbedder[SupportDTO]):

    async def _embed_dtos_async(self, items, session):
        _supports = [support for support in items if "info" in support]
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
                **support, **{
                    "embeddings": {
                        "title_embeddings": title_vector,
                        "content_embeddings": content_vector,
                    }
                }
            ) for support, title_vector, content_vector in
            zip(_supports, embeddings[0], embeddings[1])
        ]
