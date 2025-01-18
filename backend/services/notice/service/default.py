from db.repositories import transaction

import asyncio
from services.notice.crawler.default import URLs
from services.notice.service import NoticeServiceBase
import logging

logger = logging.getLogger(__name__)


class NoticeService(NoticeServiceBase):

    @transaction()
    async def run_full_crawling_pipeline_async(self, **kwargs):
        department = kwargs.get("department")
        if not department:
            raise ValueError

        models = []

        url_dict = {}
        for departments in URLs.values():
            if department in departments:
                url_dict = departments[department]
                break

        reset = kwargs.get("reset", False)

        if reset:
            affected = self.notice_repo.delete_by_department(department)
            logger.info(f"[{department}] {affected} rows deleted.")

        from tqdm import tqdm
        interval = kwargs.get('interval', 30)

        for category, url in url_dict.items():
            urls = self.notice_crawler.scrape_urls(url=url)

            pbar = tqdm(
                range(0, len(urls), interval),
                total=len(urls),
                desc=f"[{department}-{category}]"
            )

            for st in pbar:
                ed = st + interval
                pbar.set_postfix({'range': f"{st} ~ {ed}"})

                _urls = urls[st:ed]
                notices = await self.notice_crawler.scrape_partial_async(
                    urls=_urls, category=category, department=department
                )
                #if kwargs.get('with_embeddings', True):
                notices = await self.notice_embedder.embed_all_async(
                    items=notices, interval=interval
                )

                notice_models = [self.dto2orm(n) for n in notices]
                notice_models = [n for n in notice_models if n]
                notice_models = self.notice_repo.create_all(notice_models)
                models += notice_models

                pbar.update(interval)

                await asyncio.sleep(kwargs.get('delay', 0))

        return models
