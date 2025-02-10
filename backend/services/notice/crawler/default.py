import asyncio
from typing import List, Optional
from aiohttp import ClientError
from markdownify import markdownify as md

from bs4 import BeautifulSoup
from services.notice.crawler.base import NoticeCrawlerBase
from urllib3.util import parse_url

from services.notice.dto import NoticeDTO

SELECTORs = {
    "list": "div._articleTable > form:nth-child(2) table > tbody > tr:not(.headline)",
    "pagination": "div._articleTable > form:nth-child(3) > div:nth-child(10) > div > ul",
    "detail": {
        "info": {
            "title": "body > div > div.artclViewTitleWrap > h2",
            "content": "body > div > div.artclView",
            "author_date": "div.artclViewHead > div.right > dl",
        },
        "attachments": "div.artclItem > dl > dd > ul > li"
    }
}


class NoticeCrawler(NoticeCrawlerBase):

    def compare_path(self, path: str, last_id: int | None):
        if not last_id:
            return True

        ss = path.split('/')[4]
        return int(ss) > int(last_id)

    def scrape_urls(self, **kwargs) -> List[str]:
        """공지 리스트에서 각 게시글 url 추출"""

        url = kwargs.get("url")
        if not url:
            raise ValueError("'url' must be contained")
        _url = parse_url(url)

        rows = kwargs.get("rows", 500)

        _url_str = f"{url}?row={rows}"
        print(_url_str)

        soup = self._scrape(_url_str, is_success=self._check_table_exists)
        tot_pages = self._get_page_num(soup)
        last_id: int | None = kwargs.get("last_id")
        urls: List[str] = []

        for page in range(0, tot_pages):
            if page > 0:
                _url_str = f"{url}?row={rows}&page={page + 1}"
                soup = self._scrape(
                    _url_str, is_success=self._check_table_exists
                )

            paths = self._parse_paths(soup)
            filtered = [
                path for path in paths if self.compare_path(path, last_id)
            ]
            _urls = [
                f"{_url.scheme}://{_url.netloc}{path}" for path in filtered
            ]

            urls += _urls

            if len(paths) > len(filtered):
                return urls

        return urls

    def _get_page_num(self, soup: BeautifulSoup) -> int:
        """공지사항 전체 페이지 수 반환"""

        pagination_container = soup.select_one(SELECTORs["pagination"])
        if not pagination_container:
            return 1

        page_list = pagination_container.select("li")

        return len(page_list)

    def _check_table_exists(self, soup: BeautifulSoup) -> bool:
        """공지사항 테이블 존재 여부 체크"""

        table = soup.select_one("table.artclTable")
        return table is not None

    def _parse_paths(self, soup: BeautifulSoup) -> List[str]:
        """공지 리스트에서 각 게시글 경로 추출"""

        table_rows = soup.select(SELECTORs['list'])

        paths: List[str] = []
        for row in table_rows:
            anchor = row.select_one("td._artclTdTitle > a")
            if anchor is None or not anchor.has_attr("href"):
                continue

            href = str(anchor["href"])
            paths.append(href)

        return paths

    def _parse_detail(self, dto, soup):
        for img in soup.select("img"):
            img.extract()

        _info = {}
        for key, selector in SELECTORs["detail"]["info"].items():
            if key in ["title", "content"]:
                element = soup.select_one(selector)
                if element is None:
                    return None

                text = element.get_text(separator=" ", strip=True)
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

                category = dt.get_text(separator=" ", strip=True)
                content = dd.get_text(separator=" ", strip=True)

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
                "name": self._preprocess_text(anchor.text),
                "url": self._preprocess_text(str(anchor["href"])),
            })

        _info = {
            **_info,
            **dto["info"]
        }
        _dto = {
            **dto, "info": _info,
            "attachments": _attachments
        }

        return NoticeDTO(**_dto)
