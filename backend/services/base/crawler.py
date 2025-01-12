from abc import abstractmethod
from typing import Generic, List, TypeVar
import re

DTO = TypeVar("DTO")


class BaseCrawler(Generic[DTO]):

    @abstractmethod
    async def scrape_all_async(self, interval: int) -> List[DTO]:
        raise NotImplementedError("method 'scrape_all_async' must be implemented before use.")

    @abstractmethod
    async def scrape_partial_async(self, st: int, ed: int) -> List[DTO]:
        raise NotImplementedError("method 'scrape_all_async' must be implemented before use.")

    def _preprocess_text(self, text: str, remove_newline: bool = False):
        """텍스트 전처리"""
        text = re.sub(r"\\+", "", text)   # 백슬래시(\\) 제거
        text = re.sub(r"\n+", "\n", text) # 여러 줄바꿈을 하나의 공백으로 대체
        text = re.sub(r"\t", "", text)    # 여러 줄바꿈을 하나의 공백으로 대체
        text = re.sub(r"\r", "", text)    # 여러 줄바꿈을 하나의 공백으로 대체
        exclude_base64 = re.compile(r"data:image/[a-zA-Z]+;base64,[^\"']+")
        text = re.sub(exclude_base64, "", text)
        if remove_newline:
            text = re.sub(r"\n", "", text)
        re.sub(r"\s+", " ", text).strip()
        return text
