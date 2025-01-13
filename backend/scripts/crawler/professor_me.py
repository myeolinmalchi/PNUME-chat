"""교수님(기계공학부) 크롤링 스크립트

Usage:
    poetry run python3 scripts/crawler/professor.py --category <category> --interval <interval>
        -i, --interval: 한 번에 스크랩 할 게시글 수 (default: 50)
        -c, --category: 공지사항 카테고리 (`services/professor/crawler.py` 참고. default: ALL)
"""

import argparse
import asyncio

from sqlalchemy import text

from db.common import get_engine
from db.repositories import transaction

from services.professor import create_professor_me_service

import logging

from services.professor.crawler import ProfessorMECrawler


@transaction()
async def main(**kwargs):
    logging.basicConfig(
        level=logging.INFO,
        format="[%(category)s] %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    professor_crawler = ProfessorMECrawler()
    professor_service = create_professor_me_service(
        professor_crawler=professor_crawler
    )

    engine = get_engine()

    try:
        with engine.connect() as conn:
            conn.execute(text("delete from professor_research_fields;"))
            conn.execute(text("delete from professor_educations;"))
            conn.execute(text("delete from professor_careers;"))
            conn.execute(text("delete from professors;"))
            conn.commit()

        await professor_service.run_full_crawling_pipeline_async(
            interval=kwargs.get('interval'),
            delay=kwargs.get('delay'),
        )
    except Exception as e:
        logging.exception(f"Error while scraping({e})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--interval", dest="interval", action="store", default="1"
    )
    parser.add_argument(
        "-d", "--delay", dest="delay", action="store", default="0"
    )
    parser.add_argument(
        "-r", "--reset", dest="reset", action="store", default="True"
    )
    args = parser.parse_args()

    kwargs = {
        "interval": int(args.interval),
        "delay": float(args.delay),
        "reset": bool(args.reset)
    }

    asyncio.run(main(**kwargs))
