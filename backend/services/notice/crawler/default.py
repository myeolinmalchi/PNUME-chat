import asyncio
from typing import List, Optional
from markdownify import markdownify as md

from bs4 import BeautifulSoup
from services.notice.crawler import NoticeCrawlerBase
from urllib3.util import parse_url
import json

from services.notice.dto import NoticeDTO

URLs = {}

SELECTORs = {
    "list": "div._articleTable > form:nth-child(2) table > tbody > tr:not(.headline)",
    "detail": {
        "info": {
            "title": "body > div > div.artclViewTitleWrap > h2",
            "date": "body > div > div.artclViewHead > div.right > dl:first-child > dd",
            "author": "body > div > div.artclViewHead > div.right > dl:nth-child(3) > dd",
            "content": "body > div > div.artclView",
        },
        "attachments": "body > div > div.artclItem.viewForm > dl > dd > ul > li:nth-child(1)"
    }
}

with open('urls/notices.json') as f:
    URLs = json.load(f)


class NoticeCrawler(NoticeCrawlerBase):

    def scrape_urls(self, **kwargs) -> List[str]:
        """게시글 url 목록 불러오기"""

        url = kwargs.get("url")
        if not url:
            raise ValueError("'url' must be contained")

        _url = f"{url}?row=1000"

        soup = self._scrape(_url)
        paths = self._parse_paths(soup)

        _url = parse_url(url)
        _urls = [f"{_url.scheme}://{_url.netloc}{path}" for path in paths]

        return _urls

    def _parse_paths(self, soup: BeautifulSoup) -> List[str]:
        table_rows = soup.select(SELECTORs['list'])

        paths: List[str] = []
        for row in table_rows:
            anchor = row.select_one("td._artclTdTitle > a")
            if anchor is None or not anchor.has_attr("href"):
                continue

            href = str(anchor["href"])
            paths.append(href)

        return paths

    async def _scrape_partial_async(self, session, **kwargs):
        category = kwargs.get('category')
        department = kwargs.get('department')
        urls = kwargs.get('urls')

        if not urls or not category or not department:
            raise ValueError

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
                notice["info"]["category"] = category
                notice["info"]["department"] = department

        notices = [notice for notice in notices if notice]

        return notices

    def _parse_detail(self, soup: BeautifulSoup) -> Optional[NoticeDTO]:
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

        return NoticeDTO(**_dto)
