import asyncio
from typing import Dict, List

from bs4 import BeautifulSoup
import re

from services.base.crawler import BaseCrawler
from utils.scrape import scrape, ascrape_all
from .dto import ProfessorDTO

import re

LIST_URL = "https://me.pusan.ac.kr/new/sub01/sub04.asp?perPage=1000"
DETAIL_URL = "https://me.pusan.ac.kr/new/sub01/sub04_detail.asp"

SELECTORs = {
    "list": "#contents > div > div > div > div.professor-box",
    "detail": {
        "name": "#contents > div > div.professor-wrapper > div > p.name",
        "name_eng": "#contents > div > div.professor-wrapper > div > p.eng_name",
        "minor": "#professor-major > dd",
        "lab_addr": "#professor-lab > dd > span",
        "office_phone": "#professor-office > dd",
        "website": "#professor-website > dd",
        "email": "#professor-email > dd",
    },
}

EDU_KEYWORDS = {
    "학사": ["학사", "학부", "B.S", "BS"],
    "석사": ["석사", "M.S", "MS"],
    "박사": ["박사", "Ph.D", "PhD"],
    "석박사통합": ["통합", "석박사"],
}


class ProfessorCrawler(BaseCrawler):

    def scrape_seqs(self) -> List[int]:
        soup = scrape(LIST_URL)
        if soup is None:
            return []

        seqs = self._parse_seqs(soup)
        return seqs

    def _parse_seqs(self, soup: BeautifulSoup) -> List[int]:
        professor_boxes = soup.select(SELECTORs["list"])

        seqs: List[int] = []
        for box in professor_boxes:
            anchor = box.select_one("& > a:first-child")
            if anchor is None or not anchor.has_attr("href"):
                continue

            href = str(anchor["href"])
            seq_str = re.search(r"seq=(\d+)", href)

            if seq_str is not None:
                seq = int(seq_str.group(1))
                seqs.append(seq)

        return seqs

    async def scrape_details_async(self, seqs: List[int]) -> Dict[int, ProfessorDTO]:
        _urls = [f"{DETAIL_URL}?seq={seq}" for seq in seqs]

        soups = await ascrape_all(_urls, 30)
        loop = asyncio.get_running_loop()
        tasks = [
            loop.run_in_executor(None, self._parse_detail, seq, soup) for seq, soup in zip(seqs, soups)
            if soup is not None
        ]

        results = await asyncio.gather(*tasks)
        results = {p["seq"]: p for p in results if p is not None}

        return results

    def _parse_detail(self, seq: int, soup: BeautifulSoup):
        elements = {key: soup.select_one(selector) for key, selector in SELECTORs["detail"].items()}

        basic_info = {k: v.get_text(separator="", strip=True) for k, v in elements.items() if v is not None}

        additional_info = {}

        contents_boxes = soup.select("#contents > div > div.contents-box")

        for box in contents_boxes:
            title_element = box.select_one("& > .title01")
            if title_element is None:
                continue

            title = title_element.get_text(strip=True)
            items = title_element.select(".ul-list01 > li")

            if "연구 분야" in title:
                additional_info["fields"] = [{
                    "seq": idx + 1,
                    "name": field.get_text(strip=True)
                } for idx, field in enumerate(items)]

            elif "학력" in title:
                educations = []
                for idx, e in enumerate(items):
                    text = e.get_text(strip=True)
                    education = {"seq": idx + 1, "name": text}

                    for _type, keywords in EDU_KEYWORDS.items():
                        if any(keyword in text for keyword in keywords):
                            education["edu_type"] = _type
                            break

                    educations.append(education)

                additional_info["educations"] = educations

            elif "경력" in title:
                additional_info["fields"] = [{
                    "seq": idx + 1,
                    "name": career.get_text(strip=True)
                } for idx, career in enumerate(items)]

        for img in soup.select("img"):
            img.extract()

        result = ProfessorDTO(**{
            "seq": seq,
            "basic_info": basic_info,
            "additional_info": additional_info,
        })

        return result

    async def scrape_all_async(self, interval: int) -> List[ProfessorDTO]:
        seqs = self.scrape_seqs()

        results: List[ProfessorDTO] = []

        for st_idx in range(0, len(seqs), interval):
            ed_idx = st_idx + interval
            _seqs = seqs[st_idx:ed_idx]
            professors = await self.scrape_details_async(_seqs)
            results += professors.values()

        return results
