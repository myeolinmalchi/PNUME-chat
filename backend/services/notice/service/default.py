from typing import List, cast
from tqdm import tqdm
from urllib3.util import parse_url
from config.config import get_notice_urls
from db.models.notice import NoticeModel
from db.repositories import transaction

import asyncio
from services.notice.dto import NoticeDTO, NoticeInfoDTO
from services.notice.service.base import NoticeServiceBase
from config.logger import _logger

import logging

logger = _logger(__name__)


class NoticeService(NoticeServiceBase):

    @transaction()
    async def run_crawling_pipeline(self, **kwargs):
        department = kwargs.get("department")
        if not department:
            raise ValueError("'department' must be provided")

        url_dict = get_notice_urls(department)

        reset = kwargs.get("reset", False)
        interval = kwargs.get('interval', 30)
        rows = kwargs.get('rows', 500)

        if interval > rows:
            interval = rows

        models: List[NoticeModel] = []

        for category, url in url_dict.items():
            try:
                search_filter = {"departments": [department], "categories": [category]}

                last_id = None
                if reset:
                    affected = self.notice_repo.delete_all(**search_filter)
                    logger(f"[{department}-{category}] {affected} rows deleted.")

                else:
                    last_notice = self.notice_repo.find_last_notice(**search_filter)
                    if last_notice:
                        last_path = parse_url(last_notice.url).path
                        if not last_path:
                            raise ValueError(f"잘못된 url입니다: {last_notice.url}")
                        last_id = int(last_path.split("/")[4])

                urls = await self.notice_crawler.scrape_urls_async(
                    url=url, rows=rows, last_id=last_id
                )

                with tqdm(total=len(urls), desc=f"[{department}-{category}]") as pbar:
                    for st in range(0, len(urls), interval):
                        ed = min(st + interval, len(urls))
                        pbar.set_postfix({'range': f"{st + 1}-{ed}"})

                        def add_info(notice: NoticeDTO, **kwargs) -> NoticeDTO:
                            info = notice["info"]
                            info = cast(NoticeInfoDTO, {**info, **kwargs})
                            return {**notice, "info": info}

                        notices = await self.notice_crawler.scrape_detail_async(urls[st:ed])
                        notices = map(
                            lambda n: add_info(n, department=department, category=category),
                            notices,
                        )
                        notices = await self.notice_embedder.embed_dtos_batch_async(
                            dtos=list(notices), batch_size=interval
                        )

                        notice_models = [self.dto2orm(n) for n in notices]
                        notice_models = [n for n in notice_models if n]
                        notice_models = self.notice_repo.create_all(notice_models)
                        models += notice_models

                        await asyncio.sleep(kwargs.get('delay', 0))

                        pbar.update(len(notice_models))

            except TimeoutError as e:
                #affected = self.notice_repo.delete_by_department(department)
                logger(f"[{department}-{category}] 크롤링에 실패하였습니다.", level=logging.ERROR)
                raise e

        return [self.orm2dto(orm) for orm in models]
