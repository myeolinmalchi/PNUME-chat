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
        for img in soup.select("img"):
            img.extract()

        _info = {}
        for key, selector in SELECTORs["detail"]["info"].items():
            if key in ["title", "content"]:
                element = soup.select_one(selector)
                if element is None:
                    return None

                text = element.get_text(separator="", strip=True)
                if key == "content":
                    text = self._preprocess_text(md(text))
                _info[key] = text
                continue

            dls = soup.select(selector)
            for dl in dls:
                dt = dl.select_one("dt:first-child")
                dd = dl.select_one("dd:nth-child(2)")
                if not dt or not dd:
                    continue

                category = dt.get_text(separator="", strip=True)
                content = dd.get_text(separator="", strip=True)

                if category in ["작성일", "date"]:
                    _info["date"] = content

                if category in ["작성자", "name"]:
                    _info["author"] = content

        attachment_elements = soup.select(SELECTORs["detail"]["attachments"])

        _attachments = []
        for e in attachment_elements:
            anchor = e.select_one("a")
            if not anchor or not anchor.has_attr("href"):
                continue

            _attachments.append({
                "name": self._preprocess_text(anchor.text, True),
                "url": self._preprocess_text(str(anchor["href"]), True),
            })

        _dto = {"info": _info, "attachments": _attachments}

        return NoticeDTO(**_dto)
