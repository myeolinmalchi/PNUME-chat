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
from db.repositories import transaction
from services.notice_me import NoticeMECrawler, URLs, NoticeMEService
import logging

from services.notice_me.embedder import NoticeMEEmbedder


@transaction()
async def main(**kwargs):
    logging.basicConfig(
        level=logging.INFO,
        format="[%(category)s] %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    category = kwargs.get('category', 'ALL')

    if category not in URLs.keys() and category != "ALL":
        raise Exception("존재하지 않는 카테고리입니다.")

    notice_repo = NoticeMERepository()
    notice_embedder = NoticeMEEmbedder()
    notice_crawler = NoticeMECrawler()
    notice_service = NoticeMEService(
        notice_repo, notice_embedder, notice_crawler
    )

    categories = {**URLs} if category == "ALL" else {category: URLs[category]}
    engine = get_engine()

    reset = kwargs.get('reset', True)

    for url_key in categories.keys():

        if reset:
            with engine.connect() as conn:
                conn.execute(
                    text(f"delete from notices where category = '{url_key}';")
                )
                conn.commit()

        try:
            await notice_service.run_full_crawling_pipeline_async(
                url_key=url_key,
                interval=kwargs.get('interval'),
                delay=kwargs.get('delay'),
                with_embeddings=True
            )
        except Exception as e:
            logging.exception(
                f"Error while scraping({e})",
                extra={
                    "category": url_key,
                },
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--interval", dest="interval", action="store", default="10"
    )
    parser.add_argument(
        "-d", "--delay", dest="delay", action="store", default="0"
    )
    parser.add_argument(
        "-c", "--category", dest="category", action="store", default="ALL"
    )
    parser.add_argument(
        "-r", "--reset", dest="reset", action="store", default="True"
    )
    args = parser.parse_args()

    kwargs = {
        "interval": int(args.interval),
        "delay": float(args.delay),
        "category": str(args.category),
        "reset": bool(args.reset)
    }

    asyncio.run(main(**kwargs))
