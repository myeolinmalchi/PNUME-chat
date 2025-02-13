from tqdm import tqdm
from urllib3.util import parse_url
from config.config import get_notice_urls
from db.repositories import transaction

import asyncio
from services.notice.dto import NoticeDTO
from services.notice.service.base import NoticeServiceBase
import logging

logger = logging.getLogger(__name__)


class NoticeService(NoticeServiceBase):

    @transaction()
    async def run_full_crawling_pipeline_async(self, **kwargs):
        department = kwargs.get("department")
        if not department:
            raise ValueError

        models = []

        url_dict = get_notice_urls(department)

        reset = kwargs.get("reset", False)
        if reset:
            affected = self.notice_repo.delete_by_department(department)
            logger.info(f"[{department}] {affected} rows deleted.")

        interval = kwargs.get('interval', 30)
        rows = kwargs.get('rows', 500)

        if interval > rows:
            interval = rows

        try:
            for category, url in url_dict.items():
                if not reset:
                    last_notice = self.notice_repo.find_last_notice(
                        departments=[department], categories=[category]
                    )
                    if last_notice:
                        _last_url = parse_url(last_notice.url)
                        _last_path = _last_url.path
                        if not _last_path:
                            raise ValueError(f"잘못된 url입니다: {_last_url.url}")

                        _last_id = int(_last_path.split("/")[4])
                        urls = self.notice_crawler.scrape_urls(
                            url=url,
                            rows=rows,
                            **({
                                "last_id": _last_id
                            } if last_notice else {})
                        )
                    else:
                        urls = self.notice_crawler.scrape_urls(
                            url=url, rows=rows
                        )
                else:
                    urls = self.notice_crawler.scrape_urls(url=url, rows=rows)

                pbar = tqdm(
                    range(0, len(urls), interval),
                    total=len(urls),
                    desc=f"[{department}-{category}]"
                )

                for st in pbar:
                    ed = min(st + interval, len(urls))
                    pbar.set_postfix({
                        'range': f"{st + 1} ~ {ed}"
                    })

                    _urls = urls[st:ed]
                    dtos = [
                        NoticeDTO(
                            **{
                                "url": url,
                                "info": {
                                    "department": department,
                                    "category": category
                                }
                            }
                        ) for url in _urls
                    ]
                    notices = await self.notice_crawler.scrape_detail_async(
                        dtos
                    )
                    notices = await self.notice_embedder.embed_dtos_batch_async(
                        items=notices, batch_size=interval
                    )

                    notice_models = [self.dto2orm(n) for n in notices]
                    notice_models = [n for n in notice_models if n]
                    notice_models = self.notice_repo.create_all(notice_models)
                    models += notice_models

                    pbar.update(interval)

                    await asyncio.sleep(kwargs.get('delay', 0))
        except TimeoutError as e:
            affected = self.notice_repo.delete_by_department(department)
            logger.exception(
                f"[{department}] 크롤링에 실패하여 이전 데이터를 초기화 했습니다. ({affected} row deleted)"
            )
            raise e

        return models

if __name__ == '__main__':
    print('adsf')