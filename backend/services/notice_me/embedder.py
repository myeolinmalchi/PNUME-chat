import asyncio
from typing import List

from services.base.embedder import BaseEmbedder
from services.notice_me.dto import NoticeMEDTO


class NoticeMEEmbedder(BaseEmbedder[NoticeMEDTO]):

    async def _embed_all_async(self, items, interval, session):

        def parts(_list, n):
            for idx in range(0, len(_list), n):
                yield _list[idx:idx + n]

        parted_notices = list(parts(items, interval))

        notices: List[NoticeMEDTO] = []

        async def embed_partial_async(_notices: List[NoticeMEDTO]):
            _notices = [notice for notice in _notices if "info" in notice]
            _infos = [notice["info"] for notice in _notices if "info" in notice]

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

            embeddings = await asyncio.gather(
                titles_coroutine, contents_coroutine
            )

            return [
                NoticeMEDTO(
                    **notice, **{
                        "embeddings": {
                            "title_embeddings": title_vector,
                            "content_embeddings": content_vector,
                        }
                    }
                ) for notice, title_vector, content_vector in
                zip(_notices, embeddings[0], embeddings[1])
            ]

        for _notices in parted_notices:
            notices += await embed_partial_async(_notices)

        return notices
