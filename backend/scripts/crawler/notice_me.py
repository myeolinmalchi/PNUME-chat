"""공지사항(기계공학부) 게시글 크롤링 스크립트

Usage:
    poetry run python3 scripts/crawler/notice_me.py --category <category> --interval <interval>
        -i, --interval: 한 번에 스크랩 할 게시글 수 (default: 50)
        -c, --category: 공지사항 카테고리 (`services/notice_me/crawler.py` 참고. default: ALL)
"""

import argparse
import asyncio

from sqlalchemy import text

from db.common import get_engine
from db.repositories import NoticeMERepository
from db.repositories.base import transaction
from services.notice_me import NoticeMECrawler, URLs, NoticeMEService
import logging


@transaction()
async def run(interval: int, category: str):
    logging.basicConfig(
        level=logging.INFO,
        format="[%(category)s] %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    if category not in URLs.keys() and category != "ALL":
        raise Exception("존재하지 않는 카테고리입니다.")

    notice_repo = NoticeMERepository()
    notice_service = NoticeMEService(notice_repo)
    notice_crawler = NoticeMECrawler()

    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("delete from notice_attachments;"))
        conn.execute(text("delete from notice_content_chunks;"))
        conn.execute(text("delete from notices;"))
        conn.commit()

    categories = URLs.keys() if category == "ALL" else [category]

    for url_key in categories:
        try:
            seq = notice_crawler.fetch_last_seq(url_key)
            logging.info(
                f"마지막 게시글: {seq}",
                extra={
                    "category": url_key,
                },
            )
            if seq is None:
                raise Exception(f"마지막 게시글 번호를 불러오지 못했습니다.")

            notices = await notice_crawler.ascrape_all(url_key, interval)
            notices = list(notices.values())
            notices = [notice for notice in notices if "info" in notice]
            notice_service.create_notices(url_key, notices)
        except Exception:
            logging.exception(
                "Error while scraping",
                extra={
                    "category": url_key,
                },
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--interval", dest="interval", action="store", default="50"
    )
    parser.add_argument(
        "-c", "--category", dest="category", action="store", default="ALL"
    )
    args = parser.parse_args()

    interval = int(args.interval)
    category = str(args.category)
    asyncio.run(run(interval, category))
