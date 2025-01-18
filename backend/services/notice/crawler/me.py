import asyncio
from typing import List, Optional

from bs4 import BeautifulSoup
from markdownify import markdownify as md

from services.notice import NoticeDTO

import re

from services.notice.crawler.base import NoticeCrawlerBase

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
        "path": "/new/sub05/sub02.asp",
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

DOMAIN = "https://me.pusan.ac.kr"
DEPARTMENT = "기계공학부"


class NoticeMECrawler(NoticeCrawlerBase):

    def scrape_urls(self, **kwargs) -> List[str]:
        """게시글 url 목록 불러오기"""
        url_key = kwargs.get("url_key")
        if not url_key:
            raise ValueError("'url_key' must be contained")
        if url_key not in URLs.keys():
            raise ValueError("존재하지 않는 카테고리입니다.")

        url = f"{DOMAIN}{URLs[url_key]['path']}"

        soup = self._scrape(url)
        seq = self._parse_last_seq(soup)

        path = URLs[url_key]["path"]
        db = URLs[url_key]["db"]

        _urls = [
            f"{DOMAIN}{path}?db={db}&seq={seq}&page_mode=view"
            for seq in range(1, seq + 1)
        ]

        return _urls

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

    async def _scrape_partial_async(self, session, **kwargs):
        urls = kwargs.get('urls')
        if not urls:
            raise ValueError("parameter 'urls' must be contained")

        url_key = kwargs.get('url_key')

        if not url_key:
            raise ValueError(f"parameter 'url_key' must be contained")
        if url_key not in URLs:
            raise ValueError(f"존재하지 않는 카테고리입니다.({url_key})")

        soups = await self._scrape_async(urls, session=session)
        loop = asyncio.get_running_loop()
        tasks = [
            loop.run_in_executor(None, self._parse_detail, soup)
            for soup in soups
        ]
        notices = await asyncio.gather(*tasks)

        for notice, url in zip(notices, urls):
            if notice and "info" in notice:
                notice["url"] = url
                notice["info"]["category"] = url_key
                notice["info"]["department"] = DEPARTMENT

        notices = [notice for notice in notices if notice]

        return notices

    def _parse_detail(
        self,
        soup: BeautifulSoup,
    ) -> Optional[NoticeDTO]:
        for img in soup.select("img"):
            img.extract()

        elements = {
            key: soup.select_one(selector)
            for key, selector in SELECTORs["detail"]["info"].items()
        }

        _info = {
            key: element.get_text(separator="", strip=True)
            for key, element in elements.items() if element is not None
        }

        if "content" not in _info or "title" not in _info:
            return None

        att_element = soup.select_one(SELECTORs["detail"]["attachments"])

        _attachments = []
        if att_element:
            for a in att_element.select("a"):
                if not a or not a.has_attr("href"):
                    continue

                name = self._preprocess_text(a.text, True)
                path = self._preprocess_text(str(a["href"]), True),
                _attachments.append({"name": name, "url": f"{DOMAIN}{path}"})

        _info["content"] = self._preprocess_text(md(_info["content"]))
        _dto = {"info": _info, "attachments": _attachments}

        return NoticeDTO(**_dto)
