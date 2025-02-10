from db.repositories import transaction

import asyncio
from services.notice.dto import NoticeDTO
from services.notice.service.base import NoticeServiceBase

import logging

logger = logging.getLogger(__name__)


class NoticeMEService(NoticeServiceBase):

    @transaction()
    async def run_full_crawling_pipeline_async(self, **kwargs):

        models = []

        url_key = kwargs.get('url_key', '')
        urls = self.notice_crawler.scrape_urls(url_key=url_key)
        interval = kwargs.get('interval', 30)
        from tqdm import tqdm

        reset = kwargs.get("reset", False)

        if reset:
            affected = self.notice_repo.delete_by_department("기계공학부")
            logger.info(f"[기계공학부] {affected} rows deleted.")

        pbar = tqdm(
            range(0, len(urls), interval),
            total=len(urls),
            desc=f"[기계공학부-{url_key}]",
        )
        for st in pbar:
            ed = min(st + interval, len(urls))
            pbar.set_postfix({
                'range': f"{st + 1} ~ {ed}",
            })

            _urls = urls[st:ed]
            dtos = [
                NoticeDTO(
                    **{
                        "url": url,
                        "info": {
                            "department": "기계공학부",
                            "category": url_key
                        }
                    }
                ) for url in _urls
            ]
            notices = await self.notice_crawler.scrape_detail_async(dtos)
            if kwargs.get('with_embeddings', True):
                notices = await self.notice_embedder.embed_dtos_batch_async(
                    items=notices, batch_size=interval
                )

            notice_models = [self.dto2orm(n) for n in notices]
            notice_models = [n for n in notice_models if n]
            notice_models = self.notice_repo.create_all(notice_models)
            models += notice_models

            pbar.update(interval)

            await asyncio.sleep(kwargs.get('delay', 0))

        return models
