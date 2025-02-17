from abc import abstractmethod
from typing import List
from services.base import BaseCrawler
from services.notice.dto import NoticeDTO


class NoticeCrawlerBase(BaseCrawler[NoticeDTO]):

    @abstractmethod
    async def scrape_urls_async(self, **kwargs) -> List[str]:
        pass
