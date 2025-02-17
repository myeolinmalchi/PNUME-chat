from typing import Callable, List
from aiohttp import ClientSession

from bs4 import BeautifulSoup
from services.base.crawler.crawler import ParseHTMLException
from services.notice.crawler.base import NoticeCrawlerBase
from urllib3.util import parse_url

from services.base.crawler import scrape, preprocess
from services.notice.dto import NoticeDTO

SELECTORs = {
    "list": "div._articleTable > form:nth-child(2) table > tbody > tr:not(.headline)",
    "detail": {
        "info": {
            "title": "div.artclViewTitleWrap > h2",
            "content": "div.artclView",
            "author_date": "div.artclViewHead > div.right > dl",
        },
        "attachments": "div.artclItem > dl > dd > ul > li"
    }
}


def _compare_path(path: str, last_id: int | None):
    if not last_id:
        return True

    ss = path.split('/')[4]
    return int(ss) > int(last_id)


def _parse_paths(soup: BeautifulSoup) -> ParseHTMLException | List[str]:
    """공지 리스트에서 각 게시글 경로 추출"""

    table = soup.select_one("table")
    if not table:
        return ParseHTMLException("테이블이 존재하지 않습니다.")

    table_rows = soup.select(SELECTORs['list'])

    paths: List[str] = []
    for row in table_rows:
        anchor = row.select_one("td._artclTdTitle > a")
        if anchor is None or not anchor.has_attr("href"):
            continue

        href = str(anchor["href"])
        paths.append(href)

    return paths


async def _fetch_total_pages(
    index_url: str, batch_size: int, rows: int, filter: Callable[[str], bool],
    session: ClientSession
):
    """전체 게시글 경로 추출"""

    total_paths: List[str] = []
    st, ed = 0, batch_size
    while True:
        urls = [f"{index_url}?row={rows}&page={page + 1}" for page in range(st, ed)]
        results = await scrape.scrape_async(
            url=urls, session=session, post_process=_parse_paths, delay_range=(1, 2)
        )
        paths: List[str] = []
        errors: List[Exception] = []
        for result in results:
            if isinstance(result, BaseException):
                errors.append(result)
                continue
            paths += result

        if len(errors) > 0:
            raise ExceptionGroup("크롤링 중 오류가 발생했습니다.", errors)

        paths = [path for path in paths if filter(path)]
        total_paths += paths
        if len(paths) < len(urls):
            break

        st, ed = st + batch_size, ed + batch_size

    return total_paths


class NoticeCrawler(NoticeCrawlerBase):

    async def scrape_urls_async(self, **kwargs) -> List[str]:
        """공지 리스트에서 각 게시글 url 추출"""

        url = kwargs.get("url")
        rows = kwargs.get("rows", 500)
        batch_size = kwargs.get("batch_size", 5)

        if not url:
            raise ValueError("'url' must be provided")
        session = kwargs.get("session")
        if not session:
            raise ValueError("'session' must be provided")

        _url = parse_url(url)

        last_id: int | None = kwargs.get("last_id")
        paths = await _fetch_total_pages(
            url,
            batch_size,
            rows,
            filter=lambda path: _compare_path(path, last_id),
            session=session
        )

        return [f"{_url.scheme}://{_url.netloc}{path}" for path in paths]

    def _parse_detail(self, soup):

        info, img_urls = {}, []
        for key, selector in SELECTORs["detail"]["info"].items():
            match (key, soup.select(selector)):
                case (_, []):
                    return ParseHTMLException("공지사항 상세 정보 파싱에 실패했습니다.")

                case ("title", [element, *_]):
                    info["title"] = element.get_text(separator=" ", strip=True)

                case ("content", [element, *_]):
                    for img in element.select("img"):
                        if hasattr(img, "src"):
                            img_urls.append(str(img["src"]))
                    info["content"] = str(preprocess.clean_html(str(element)))

                case (_, dls):
                    for dl in dls:
                        dt = dl.select_one("dt:first-child")
                        dd = dl.select_one("dd:nth-child(2)")

                        if not dt or not dd:
                            continue

                        category = dt.get_text(separator=" ", strip=True)
                        content = dd.get_text(separator=" ", strip=True)

                        if category in ["작성일", "date"]:
                            info["date"] = content

                        if category in ["작성자", "name"]:
                            info["author"] = content

        atts = []

        atts += [{"name": info["title"], "url": url} for url in img_urls]

        for e in soup.select(SELECTORs["detail"]["attachments"]):
            anchor = e.select_one("a")
            if not anchor or not anchor.has_attr("href"):
                continue

            atts.append({
                "name": preprocess.preprocess_text(anchor.text),
                "url": preprocess.preprocess_text(str(anchor["href"])),
            })

        return NoticeDTO(**{"info": info, "attachments": atts})
