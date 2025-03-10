from abc import abstractmethod
from typing import List
from services.professor import ProfessorDTO
from services.base.crawler import BaseCrawler

EDU_KEYWORDS = {
    "학사": ["학사", "학부", "B.S", "BS"],
    "석사": ["석사", "M.S", "MS"],
    "박사": ["박사", "Ph.D", "PhD"],
    "석박사통합": ["통합", "석박사"],
}


class ProfessorCrawlerBase(BaseCrawler[ProfessorDTO]):

    @abstractmethod
    def scrape_urls(self, **kwargs) -> List[str]:
        pass
