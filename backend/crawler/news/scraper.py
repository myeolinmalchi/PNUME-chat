import asyncio
from typing import Optional, List

from bs4 import BeautifulSoup
from common import afetch_all, fetch
from models.News import News
from news.urls import urls
from markdownify import markdownify as md
import re

list_selector = "#contents > div > div > div > div.board-list02 > table > tbody > tr"


def parse_last_seq(soup: BeautifulSoup):
    table_rows = soup.select(list_selector)

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


def fetch_last_seq(url_key: str) -> Optional[int]:
    """가장 최근에 올라온 게시글 seq 반환"""
    if url_key not in urls:
        return

    soup = fetch(urls[url_key]["path"])
    return None if soup is None else parse_last_seq(soup)


detail_selectors = {
    "title": "#contents > div > div > div.board-view > dl:nth-child(1) > dd",
    "date": "#contents > div > div > div.board-view > dl:nth-child(2) > dd",
    "author": "#contents > div > div > div.board-view > dl:nth-child(3) > dd",
    "attatchments": "#contents > div > div > div.board-view > dl.half-box01.none > dd",
    "contents": "#contents > div > div > div.board-contents.clear",
}


def preprocess_text(text: str):
    text = re.sub(r"\\+", "", text)  # 백슬래시(\\) 제거
    text = re.sub(r"\n+", "\n", text)  # 여러 줄바꿈을 하나의 공백으로 대체
    re.sub(r"\s+", " ", text).strip()
    return text


def parse_detail(soup: BeautifulSoup):
    result: News = {
        "title": "",
        "date": "",
        "author": "",
        "attatchments": [],
        "contents": "",
    }

    for key, selector in detail_selectors.items():
        element = soup.select_one(selector)

        if element is None:
            continue

        for i in element.select("img"):
            i.extract()

        if key == "attatchments":
            temp = []
            anchors = element.select("a")
            for a in anchors:
                temp.append({"name": a.text, "link": a["href"][0]})

            result[key] = temp

        if key == "contents":
            result[key] = preprocess_text(md(element.decode_contents()))
            continue

        result[key] = element.get_text(separator="", strip=True)

    return result


def fetch_detail(url_key: str, seq: int) -> Optional[News]:
    """게시글 세부 정보 추출"""
    if url_key not in urls:
        return

    path = urls[url_key]["path"]
    db = urls[url_key]["db"]

    soup = fetch(f"{path}?db={db}&seq={seq}&page_mode=view")
    return None if soup is None else parse_detail(soup)


async def afetch_details(
    url_key: str, st_seq: int, ed_seq: int
) -> Optional[List[News]]:
    if url_key not in urls:
        return

    path = urls[url_key]["path"]
    db = urls[url_key]["db"]

    _urls = [
        f"{path}?db={db}&seq={seq}&page_mode=view" for seq in range(st_seq, ed_seq + 1)
    ]

    soups = await afetch_all(_urls, 30)
    loop = asyncio.get_running_loop()
    tasks = [
        loop.run_in_executor(None, parse_detail, soup)
        for soup in soups
        if soup is not None
    ]

    return await asyncio.gather(*tasks)
