import asyncio

from services.base import BaseEmbedder
from services.base.embedder import embed_async
from services.notice import NoticeDTO


class NoticeEmbedder(BaseEmbedder[NoticeDTO]):

    async def _embed_dtos_async(self, dtos, session, **kwargs):
        _notices = [notice for notice in dtos if "info" in notice]
        _infos = [notice["info"] for notice in _notices]

        titles_future = embed_async(
            texts=[_info["title"] for _info in _infos],
            session=session,
            chunking=False,
        )
        contents_future = embed_async(
            texts=[_info["content"] for _info in _infos],
            session=session,
            chunking=True,
        )

        embeddings = await asyncio.gather(titles_future, contents_future)

        return [
            NoticeDTO(
                **notice, **{
                    "embeddings": {
                        "title_embeddings": title_vector,
                        "content_embeddings": content_vector,
                    }
                }
            )
            for notice, title_vector, content_vector in zip(_notices, embeddings[0], embeddings[1])
        ]
