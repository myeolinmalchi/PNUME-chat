import asyncio

from services.base import BaseEmbedder
from services.notice import NoticeDTO


class NoticeEmbedder(BaseEmbedder[NoticeDTO]):

    async def _embed_dtos_async(self, items, session):
        _notices = [notice for notice in items if "info" in notice]
        _infos = [notice["info"] for notice in _notices]

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
            NoticeDTO(
                **notice, **{
                    "embeddings": {
                        "title_embeddings": title_vector,
                        "content_embeddings": content_vector,
                    }
                }
            ) for notice, title_vector, content_vector in
            zip(_notices, embeddings[0], embeddings[1])
        ]
