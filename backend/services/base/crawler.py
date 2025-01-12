from abc import abstractmethod
from typing import Generic, List, TypeVar
import re

DTO = TypeVar("DTO")


class BaseCrawler(Generic[DTO]):
    async def scrape_all_async(
        self,
        interval: int,
        delay: float = 0,
        session: Optional[ClientSession] = None,
        **kwargs
    ) -> List[DTO]:
        if session is None:
            raise ValueError("parameter 'session' cannot be None.")

        return await self._scrape_all_async(
            interval, delay, **kwargs, session=session
        )

    @abstractmethod
    async def _scrape_all_async(
        self, interval: int, delay: float, session: ClientSession, **kwargs
    ) -> List[DTO]:
        pass

    async def scrape_partial_async(
        self,
        seqs: List[int],
        session: Optional[ClientSession] = None,
        **kwargs
    ) -> List[DTO]:
        if session is None:
            raise ValueError("parameter 'session' cannot be None.")

        return await self._scrape_partial_async(seqs, **kwargs, session=session)

    @abstractmethod
    async def _scrape_partial_async(
        self, seqs: List[int], session: ClientSession, **kwargs
    ) -> List[DTO]:
        pass

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
