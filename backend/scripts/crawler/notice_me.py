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

    from tqdm import tqdm

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

            scrape_result = await notice_crawler.ascrape_all(url_key, interval, to=-1)
            notices, title_embeddings, content_embeddings = scrape_result

            logging.info(
                f"게시글 수: {len(notices)}",
                extra={
                    "category": url_key,
                },
            )
            notices = [notice for notice in notices if notice is not None]
            content_lengths = [len(notice["content"]) for notice in notices]
            max_length = max(content_lengths)
            logging.info(
                f"최대 본문 길이: {max_length}",
                extra={
                    "category": url_key,
                },
            )

            notice_service.create_notices(
                url_key, notices, title_embeddings, content_embeddings
            )
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
