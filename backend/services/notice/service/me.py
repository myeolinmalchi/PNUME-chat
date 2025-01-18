from db.repositories import transaction

import asyncio
from services.notice.service.base import NoticeServiceBase


class NoticeMEService(NoticeServiceBase):

    @transaction()
    async def run_full_crawling_pipeline_async(self, **kwargs):

        models = []

        url_key = kwargs.get('url_key', '')
        urls = self.notice_crawler.scrape_urls(url_key=url_key)
        interval = kwargs.get('interval', 30)
        from tqdm import tqdm

        pbar = tqdm(
            range(0, len(urls), interval),
            total=len(urls),
            desc=f"[{url_key}]",
        )
        for st in pbar:
            ed = st + interval - 1

            _urls = urls[st:ed + 1]
            notices = await self.notice_crawler.scrape_partial_async(
                urls=_urls, url_key=url_key
            )
            if kwargs.get('with_embeddings', True):
                notices = await self.notice_embedder.embed_all_async(
                    items=notices, interval=interval
                )

            notice_models = [self.dto2orm(n) for n in notices]
            notice_models = [n for n in notice_models if n]
            notice_models = self.notice_repo.create_all(notice_models)
            models += notice_models

            pbar.update(interval)
            pbar.set_postfix({
                'range': f"{st} ~ {ed}",
            })

            await asyncio.sleep(kwargs.get('delay', 0))

        return models
