from datetime import time
from typing import List, Optional

from bs4 import BeautifulSoup
from services.professor.crawler.base import ProfessorCrawlerBase
from urllib3.util import parse_url
import asyncio

from markdownify import markdownify as md

from services.professor import ProfessorDTO

SELECTORs = {
    "list": "ul._prFlList > li",
    "detail": {
        "name": "div.artclInfo > div:first-child > strong",
        "common": "div.artclInfo > dl",
        "profile_img": "div.thumbnail > img",
        "attachments": "div.artclItem > dl > dd > ul > li"
    }
}

INFO_MAP = {
    "name_eng": ["영문이름"],
    "email": ["이메일"],
    "office_phone": ["전화번호"],
    "website": ["사이트"],
    "lab_addr": ["사무실"],
    "major": ["연구분야", "전공"],
}


class ProfessorCrawler(ProfessorCrawlerBase):

    def scrape_urls(self, **kwargs) -> List[str]:
        """교수님 리스트에서 url 추출"""
        url = kwargs.get("url")
        if not url:
            raise ValueError("'url' must be contained")

        soup = self._scrape(url)
        paths = self._parse_paths(soup)

        _url = parse_url(url)
        urls = [f"{_url.scheme}://{_url.netloc}{path}" for path in paths]

        return urls

    def _parse_paths(self, soup: BeautifulSoup) -> List[str]:
        """교수님 리스트에서 상세 페이지 경로 추출"""
        table_rows = soup.select(SELECTORs["list"])

        paths: List[str] = []
        for row in table_rows:
            anchor = row.select_one("div.artclInfo > div > a")
            if anchor is None or not anchor.has_attr("href"):
                continue

            href = str(anchor["href"])
            paths.append(href)

        return paths

    async def _scrape_partial_async(self, session, **kwargs):
        department = kwargs.get('department')
        urls = kwargs.get('urls')

        if not urls or not department:
            raise ValueError

        soups = await self._scrape_async(urls, session=session)
        loop = asyncio.get_running_loop()
        tasks = [
            loop.run_in_executor(None, self._parse_detail, soup)
            for soup in soups
        ]

        professors = await asyncio.gather(*tasks)

        for professor, url in zip(professors, urls):
            if professor and "info" in professor:
                professor["url"] = url
                professor["info"]["department"] = department

        professors = [professor for professor in professors if professor]

        return professors

    def _parse_detail(self, soup: BeautifulSoup) -> Optional[ProfessorDTO]:
        """교수님 상세 정보 파싱"""

        _info = {}

        name_element = soup.select_one(SELECTORs["detail"]["name"])
        if not name_element:
            return None

        thumbnail_element = soup.select_one(SELECTORs["detail"]["profile_img"])

        if thumbnail_element and thumbnail_element.has_attr("src"):
            src = thumbnail_element["src"]
            _info["profile_img"] = str(src)

        _info["name"] = self._preprocess_text(name_element.text, True)

        common_elements = soup.select(SELECTORs["detail"]["common"])
        for e in common_elements:
            dt = e.select_one("dt")
            dd = e.select_one("dd")

            if not dt or not dd:
                continue

            category = dt.get_text(separator="", strip=True)
            content = dd.get_text(separator="", strip=True)

            for key, keywords in INFO_MAP.items():
                if category in keywords:
                    _info[key] = content
                    break

        detail_elements = soup.select("div._prFlDetail")

        def preprocess(element):
            text = element.get_text(separator="", strip=True)
            return self._preprocess_text(md(text), True)

        if len(detail_elements) > 0:
            details = [preprocess(e) for e in detail_elements]
            _info["detail"] = "\n\n".join(details)

        _dto = {"info": _info, "url": ""}

        return ProfessorDTO(**_dto)
