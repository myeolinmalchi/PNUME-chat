import argparse
import asyncio

from db.repositories import NoticeMERepository
from services.notice_me import NoticeMECrawler, URLs, NoticeMEService


async def run(interval: int, category: str):
    if category not in URLs.keys() and category != "ALL":
        raise Exception("존재하지 않는 카테고리입니다.")

    notice_repo = NoticeMERepository()
    notice_service = NoticeMEService(notice_repo)
    notice_crawler = NoticeMECrawler()

    categories = URLs.keys() if category == "ALL" else [category]
    try:
        for url_key in categories:
            scrape_result = await notice_crawler.ascrape_all(url_key, interval)
            notices, title_embeddings, content_embeddings = scrape_result
            notice_service.create_notices(
                url_key, notices, title_embeddings, content_embeddings
            )
    except Exception as e:
        print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--interval", dest="interval", action="store", default="30"
    )
    parser.add_argument(
        "-c", "--category", dest="category", action="store", default="ALL"
    )
    args = parser.parse_args()

    interval = int(args.interval)
    category = str(args.category)
    asyncio.run(run(interval, category))
