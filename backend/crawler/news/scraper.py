import asyncio
from typing import Optional, List

import aiohttp
from bs4 import BeautifulSoup
from crawler.common import afetch_all, fetch
from crawler.models.Notice import Notice
from crawler.news.urls import urls
from markdownify import markdownify as md
import re

from libs.utils.embed import aembed_tei

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
    """가장 최근 게시글 seq 반환"""
    if url_key not in urls:
        raise Exception("최근 게시글 seq를 불러오지 못했습니다.")

    soup = fetch(urls[url_key]["path"])
    return None if soup is None else parse_last_seq(soup)


detail_selectors = {
    "title": "#contents > div > div > div.board-view > dl:nth-child(1) > dd",
    "date": "#contents > div > div > div.board-view > dl:nth-child(2) > dd",
    "author": "#contents > div > div > div.board-view > dl:nth-child(3) > dd",
    "attachments": "#contents > div > div > div.board-view > dl.half-box01.none > dd",
    "content": "#contents > div > div > div.board-contents.clear",
}


def preprocess_text(text: str, remove_newline: bool = False):
    """텍스트 전처리"""
    text = re.sub(r"\\+", "", text)  # 백슬래시(\\) 제거
    text = re.sub(r"\n+", "\n", text)  # 여러 줄바꿈을 하나의 공백으로 대체
    text = re.sub(r"\t", "", text)  # 여러 줄바꿈을 하나의 공백으로 대체
    text = re.sub(r"\r", "", text)  # 여러 줄바꿈을 하나의 공백으로 대체
    if remove_newline:
        text = re.sub(r"\n", "", text)
    re.sub(r"\s+", " ", text).strip()
    return text


def parse_detail(soup: BeautifulSoup):
    result: Notice = {
        "title": "",
        "date": "",
        "author": "",
        "attachments": [],
        "content": "",
    }

    elements = {
        key: soup.select_one(selector) for key, selector in detail_selectors.items()
    }

    if any(element is None for _, element in elements.items()):
        return

    # None 체크 된거라 에러 무시해도 됌
    result["title"] = elements["title"].get_text(separator="", strip=True)
    result["date"] = elements["date"].get_text(separator="", strip=True)
    result["author"] = elements["author"].get_text(separator="", strip=True)
    result["attachments"] = [
        {
            "name": preprocess_text(a.text, True),
            "url": preprocess_text(str(a["href"]), True),
        }
        for a in elements["attachments"].select("a")
    ]
    result["content"] = preprocess_text(md(elements["content"].decode_contents()))

    for img in soup.select("img"):
        img.extract()

    return result


def fetch_detail(url_key: str, seq: int) -> Optional[Notice]:
    """게시글 세부 정보 추출"""
    if url_key not in urls:
        return

    path = urls[url_key]["path"]
    db = urls[url_key]["db"]

    soup = fetch(f"{path}?db={db}&seq={seq}&page_mode=view")
    return None if soup is None else parse_detail(soup)


async def afetch_details(
    url_key: str, st_seq: int, ed_seq: int
) -> List[Optional[Notice]]:
    """게시글 세부 정보 동시 추출"""
    if url_key not in urls:
        raise Exception("존재하지 않는 URL입니다.")

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


async def aembed_all(posts: List[Notice]):
    titles = [post["title"] for post in posts]
    contents = [post["content"] for post in posts]

    semaphore = asyncio.Semaphore(4)
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(
            *[
                aembed_tei(session, semaphore, texts=titles),
                aembed_tei(session, semaphore, texts=contents),
                aembed_tei(session, semaphore, texts=titles, embed_sparse=True),
                aembed_tei(session, semaphore, texts=contents, embed_sparse=True),
            ]
        )
