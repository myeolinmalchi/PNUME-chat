from abc import abstractmethod
from typing import List
from services.base import BaseCrawler
from services.notice.dto import NoticeDTO


class NoticeCrawlerBase(BaseCrawler[NoticeDTO]):

    @abstractmethod
    def scrape_urls(self, **kwargs) -> List[str]:
        pass
