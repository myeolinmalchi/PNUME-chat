import asyncio
from typing import List, Optional

from bs4 import BeautifulSoup
from markdownify import markdownify as md
from tqdm import tqdm

from services.base.crawler import BaseCrawler

from .dto import NoticeMEDTO

import re

URLs = {
    "공지/학부": {
        "path": "/new/sub05/sub01_01.asp",
        "db": "hakbunotice"
    },
    "공지/대학원": {
        "path": "/new/sub05/sub01_02.asp",
        "db": "gradnotice"
    },
    "공지/장학": {
        "path": "/new/sub05/sub01_05.asp",
        "db": "supervision"
    },
    "공지/홍보": {
        "path": "/new/sub05/sub01_03.asp",
        "db": "notice"
    },
    "학부_소식": {
        "path": "/new/sub05/sub_02.asp",
        "db": "hakbunews"
    },
    "언론_속_학부": {
        "path": "/new/sub05/sub03.asp",
        "db": "media"
    },
    "세미나": {
        "path": "/new/sub05/sub04.asp",
        "db": "seminar"
    },
    "취업정보": {
        "path": "/new/sub05/sub05.asp",
        "db": "recruit"
    },
}

SELECTORs = {
    "list": "#contents > div > div > div > div.board-list02 > table > tbody > tr",
    "detail": {
        "info": {
            "title": "#contents > div > div > div.board-view > dl:nth-child(1) > dd",
            "date": "#contents > div > div > div.board-view > dl:nth-child(2) > dd",
            "author": "#contents > div > div > div.board-view > dl:nth-child(3) > dd",
            "content": "#contents > div > div > div.board-contents.clear",
        },
        "attachments": "#contents > div > div > div.board-view > dl.half-box01.none > dd",
    },
}


class NoticeMECrawler(BaseCrawler[NoticeMEDTO]):

    def scrape_last_seq(self, url_key: str) -> int:
        """가장 최근 게시글 seq 반환"""
        if url_key not in URLs.keys():
            raise Exception("최근 게시글 seq를 불러오지 못했습니다.")

        soup = self._scrape(URLs[url_key]["path"])
        seq = self._parse_last_seq(soup)

        return seq

    def _parse_last_seq(self, soup: BeautifulSoup):
        table_rows = soup.select(SELECTORs["list"])

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
                return seq

        raise Exception

    async def _scrape_partial_async(self, seqs, session, **kwargs):
        url_key = kwargs.get('url_key')
        if url_key not in URLs:
            raise Exception(f"존재하지 않는 카테고리입니다.({url_key})")

        path = URLs[url_key]["path"]
        db = URLs[url_key]["db"]

        _urls = [f"{path}?db={db}&seq={seq}&page_mode=view" for seq in seqs]

        soups = await self._scrape_async(_urls, session=session)
        loop = asyncio.get_running_loop()
        tasks = [
            loop.run_in_executor(None, self._parse_detail, seq, soup, url_key)
            for seq, soup in zip(seqs, soups)
        ]
        notices = await asyncio.gather(*tasks)
        notices = [notice for notice in notices if notice]

        return notices

    async def _scrape_all_async(self, interval, delay, session, **kwargs):
        url_key = kwargs.get('url_key')
        if not url_key or url_key not in URLs:
            raise ValueError("존재하지 않는 카테고리입니다.")

        seq = self.scrape_last_seq(url_key)
        results: List[NoticeMEDTO] = []

        to = kwargs.get('to', 1)
        to = seq - interval if to == -1 else to
        pbar = tqdm(
            range(seq, to, interval * -1),
            total=seq - to,
            desc=f"Scraping Notices",
        )
        for ed in pbar:
            st = ed - interval
            notices = await self.scrape_partial_async(
                list(range(st, ed)), session=session, url_key=url_key
            )
            results += notices

            pbar.update(interval)

            pbar.set_postfix({"range": f"({st}-{ed})"})
            await asyncio.sleep(delay)

        return results

    def _parse_detail(self, seq: int, soup: BeautifulSoup,
                      category: str) -> Optional[NoticeMEDTO]:
        _dto = {}

        for img in soup.select("img"):
            img.extract()

        elements = {
            key: soup.select_one(selector)
            for key, selector in SELECTORs["detail"]["info"].items()
        }

        _dto["info"] = {
            key: element.get_text(separator="", strip=True)
            for key, element in elements.items() if element is not None
        }

        if "content" not in _dto["info"] or "title" not in _dto["info"]:
            return None

        att_element = soup.select_one(SELECTORs["detail"]["attachments"])

        if att_element is not None:
            _dto["attachments"] = [{
                "name": self._preprocess_text(a.text, True),
                "url": self._preprocess_text(str(a["href"]), True),
            } for a in att_element.select("a")]

        _dto["info"]["content"] = self._preprocess_text(
            md(_dto["info"]["content"])
        )

        _dto["info"]["category"] = category

        result = NoticeMEDTO(**_dto, seq=seq)

        return result
