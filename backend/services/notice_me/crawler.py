import asyncio
from typing import Optional, List

import aiohttp
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from utils.scrape import scrape, ascrape_all
from utils.embed import EmbedResult, aembed_onnx

from .dto import NoticeMEDTO

import re


URLs = {
    "공지/학부": {"path": "/new/sub05/sub01_01.asp", "db": "hakbunotice"},
    "공지/대학원": {"path": "/new/sub05/sub01_02.asp", "db": "gradnotice"},
    "공지/장학": {"path": "/new/sub05/sub01_05.asp", "db": "supervision"},
    "공지/홍보": {"path": "/new/sub05/sub01_03.asp", "db": "notice"},
    # "공지/기자재": {
    #     "path": "/new/sub05/sub01_04.asp",
    #     "db": ""
    # },
    "학부 소식": {"path": "/new/sub05/sub_02.asp", "db": "hakbunews"},
    "언론 속 학부": {"path": "/new/sub05/sub03.asp", "db": "media"},
    "세미나": {"path": "/new/sub05/sub04.asp", "db": "seminar"},
    # "자유게시판": {
    #     "path": "/new/sub06/sub05.asp",
    #     "db": ""
    # },
    "취업정보": {"path": "/new/sub05/sub05.asp", "db": "recruit"},
}

SELECTORs = {
    "list": "#contents > div > div > div > div.board-list02 > table > tbody > tr",
    "detail": {
        "title": "#contents > div > div > div.board-view > dl:nth-child(1) > dd",
        "date": "#contents > div > div > div.board-view > dl:nth-child(2) > dd",
        "author": "#contents > div > div > div.board-view > dl:nth-child(3) > dd",
        "attachments": "#contents > div > div > div.board-view > dl.half-box01.none > dd",
        "content": "#contents > div > div > div.board-contents.clear",
    },
}


class NoticeMECrawler:
    def __init__(self):
        pass

    def fetch_last_seq(self, url_key: str) -> Optional[int]:
        """가장 최근 게시글 seq 반환"""
        if url_key not in URLs.keys():
            raise Exception("최근 게시글 seq를 불러오지 못했습니다.")

        soup = scrape(URLs[url_key]["path"])
        return None if soup is None else self._parse_last_seq(soup)

    async def afetch_details(
        self, url_key: str, st_seq: int, ed_seq: int
    ) -> List[Optional[NoticeMEDTO]]:
        """게시글 세부 정보 비동기 추출"""
        if url_key not in URLs:
            raise Exception("존재하지 않는 URL입니다.")
        if ed_seq < st_seq:
            raise Exception("'ed_seq' must be greater than or equal to 'st_seq'")

        path = URLs[url_key]["path"]
        db = URLs[url_key]["db"]

        _urls = [
            f"{path}?db={db}&seq={seq}&page_mode=view"
            for seq in range(st_seq, ed_seq + 1)
        ]

        soups = await ascrape_all(_urls, 30)
        loop = asyncio.get_running_loop()
        tasks = [
            loop.run_in_executor(None, self._parse_detail, seq, soup)
            for seq, soup in zip(range(st_seq, ed_seq + 1), soups)
            if soup is not None
        ]

        return await asyncio.gather(*tasks)

    async def ascrape_all(self, url_key: str, interval: int, to: int = 1):
        seq = self.fetch_last_seq(url_key)
        if seq is None:
            raise Exception(f"가장 최근 게시물을 불러오지 못했습니다({url_key})")

        total_notices: List[NoticeMEDTO] = []
        total_title_embeddings: List[EmbedResult | None] = []
        total_content_embeddings: List[List[EmbedResult] | None] = []

        to = seq - 1 if to == -1 else to
        for temp in range(seq, to, interval * -1):
            st, ed = temp - interval, temp
            notices = await self.afetch_details(url_key, st, ed)
            notices = [notice for notice in notices if notice is not None]

            titles = [notice["title"] for notice in notices]
            contents = [notice["content"] for notice in notices]

            timeout = aiohttp.ClientTimeout(total=6000)
            async with aiohttp.ClientSession(timeout=timeout) as sess:
                semaphore = asyncio.Semaphore(2)
                titles_coroutine = aembed_onnx(
                    session=sess,
                    semaphore=semaphore,
                    texts=titles,
                    chunking=False,
                    truncate=True,
                )
                contents_coroutine = aembed_onnx(
                    session=sess,
                    semaphore=semaphore,
                    texts=contents,
                    chunking=True,
                    truncate=False,
                )
                title_embeddings, content_embeddings = await asyncio.gather(
                    titles_coroutine, contents_coroutine
                )

                total_title_embeddings += (
                    title_embeddings
                    if title_embeddings is not None
                    else [None] * len(notices)
                )

                total_content_embeddings += (
                    content_embeddings
                    if content_embeddings is not None
                    else [None] * len(notices)
                )

            total_notices += notices

        return total_notices, total_title_embeddings, total_content_embeddings

    def _parse_last_seq(self, soup: BeautifulSoup):
        table_rows = soup.select(SELECTORs["list"])

        seq: Optional[int] = None
        for row in table_rows:
            if row.has_attr("class") and row["class"][0] == "notice":
                continue

            anchor = row.select_one("td > a:first-child")
            if anchor is None or not anchor.has_attr("href"):
                continue

            href = str(anchor["href"])
            seq_str = re.search(r"javascript:goDetail\((.*?)\)", href)

            if seq_str != None:
                seq = int(seq_str.group(1))
                break

        return seq

    def _parse_detail(self, seq: int, soup: BeautifulSoup):
        result: NoticeMEDTO = {
            "seq": seq,
            "title": "",
            "date": "",
            "author": "",
            "attachments": [],
            "content": "",
        }

        elements = {
            key: soup.select_one(selector)
            for key, selector in SELECTORs["detail"].items()
        }

        if any(element is None for _, element in elements.items()):
            return

        # 타입 체크를 위한 멋진 코드
        assert elements["title"] is not None
        assert elements["date"] is not None
        assert elements["author"] is not None
        assert elements["attachments"] is not None
        assert elements["content"] is not None

        result["title"] = elements["title"].get_text(separator="", strip=True)
        result["date"] = elements["date"].get_text(separator="", strip=True)
        result["author"] = elements["author"].get_text(separator="", strip=True)
        result["attachments"] = [
            {
                "name": self._preprocess_text(a.text, True),
                "url": self._preprocess_text(str(a["href"]), True),
            }
            for a in elements["attachments"].select("a")
        ]
        result["content"] = self._preprocess_text(
            md(elements["content"].decode_contents())
        )

        for img in soup.select("img"):
            img.extract()

        return result

    def _preprocess_text(self, text: str, remove_newline: bool = False):
        """텍스트 전처리"""
        text = re.sub(r"\\+", "", text)  # 백슬래시(\\) 제거
        text = re.sub(r"\n+", "\n", text)  # 여러 줄바꿈을 하나의 공백으로 대체
        text = re.sub(r"\t", "", text)  # 여러 줄바꿈을 하나의 공백으로 대체
        text = re.sub(r"\r", "", text)  # 여러 줄바꿈을 하나의 공백으로 대체
        exclude_base64 = re.compile(r"data:image/[a-zA-Z]+;base64,[^\"']+")
        text = re.sub(exclude_base64, "", text)
        if remove_newline:
            text = re.sub(r"\n", "", text)
        re.sub(r"\s+", " ", text).strip()
        return text
