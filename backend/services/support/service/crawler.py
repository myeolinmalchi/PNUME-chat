from db.models.support import SupportModel
from services.base.service import BaseCrawlerService
from services.support.dto import SupportDTO
from services.support.service.base import SupportService
import json
from config.logger import _logger
import asyncio

from tqdm import tqdm

logger = _logger(__name__)


# TODO: 로직 정상화
class SupportCrawlerService(SupportService, BaseCrawlerService[SupportDTO, SupportModel]):

    async def run_crawling_pipeline(self, **kwargs):
        with open("config/onestop.json", "r") as f:
            url_dict = json.load(f)

        dtos = []

        for category_key in url_dict.keys():
            sub_categories = url_dict[category_key]
            if isinstance(sub_categories, str):
                _info = {"category": category_key, "title": category_key}
                dtos.append()
                continue

            for sub_key in sub_categories.keys():
                sub_category = sub_categories[sub_key]
                if isinstance(sub_category, str):
                    info = SupportDTO(
                        info={
                            "category": category_key,
                            "sub_category": sub_key,
                            "title": sub_key
                        }, url=sub_category
                    )
                    dtos.append(info)
                    continue

                dtos_ = [
                    SupportDTO(info={
                        "category": category_key,
                        "sub_category": sub_key,
                        "title": title
                    }, url=url) for title, url in sub_category.items()
                ]

                dtos += dtos_

        interval = kwargs.get('interval', 30)

        models = []
        try:
            pbar = tqdm(range(0, len(dtos), interval), total=len(dtos))

            for st in pbar:
                ed = min(st + interval, len(dtos))
                pbar.set_postfix({'range': f"{st + 1} ~ {ed}"})
                _dtos = dtos[st:ed]
                supports = await self.support_crawler.scrape_detail_async(_dtos)
                supports = await self.support_embedder.embed_dtos_async(dtos=supports, interval=interval)
                support_models = [self.dto2orm(n) for n in supports]
                support_models = [n for n in support_models if n]
                support_models = self.support_repo.create_all(support_models)
                models += support_models

                pbar.update(interval)

                await asyncio.sleep(kwargs.get('delay', 0))

        except TimeoutError as e:
            logger(f"크롤링에 실패하였습니다.")
            logger(f"{e}")

        return [self.orm2dto(orm) for orm in models]
