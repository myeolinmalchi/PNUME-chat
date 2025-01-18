"""공지사항 게시글 크롤링 스크립트

Usage:
    poetry run python3 scripts/crawler/notice.py
        -i, --interval: 한 번에 스크랩 할 게시글 수 (default: 50)
        -d, --delay: Interval간의 딜레이 (초 단위, default: 0)
        -dp, --department: 학과 (default: ALL)
        -r, --reset: `notices` 테이블 초기화 여부 (default: true)
"""

import argparse
import asyncio
from typing import Dict, Literal

from db.repositories import transaction
import logging

from db.repositories import NoticeRepository, UniversityRepository
from services.notice import NoticeCrawler, NoticeEmbedder
from services.notice.crawler.default import URLs as DEFAULT_URLs
from services.notice.crawler.me import URLs as ME_URLs

from services.notice.crawler.me import NoticeMECrawler
from services.notice.service.default import NoticeService

import logging

from services.notice.service.me import NoticeMEService

import warnings

warnings.filterwarnings("ignore")


def init_notice_service(_type: Literal["default", "me"] = "default"):
    notice_repo = NoticeRepository()
    notice_embedder = NoticeEmbedder()
    univ_repo = UniversityRepository()
    if _type == "default":
        notice_crawler = NoticeCrawler()
        notice_service = NoticeService(
            notice_repo, notice_embedder, notice_crawler, univ_repo
        )
    elif _type == "me":
        notice_crawler = NoticeMECrawler()
        notice_service = NoticeMEService(
            notice_repo, notice_embedder, notice_crawler, univ_repo
        )

    return notice_service


@transaction()
async def main(**kwargs):

    try:
        from itertools import chain

        department = kwargs.get("department")
        departments = [[dep for dep in deps.keys()]
                       for deps in DEFAULT_URLs.values()]
        departments = list(chain(*departments)
                           ) if department == "ALL" else [department]

        _type = "me" if department == "기계공학부" else "default"

        notice_service = init_notice_service(_type)
        reset = kwargs.get("reset", False)

        if _type == "default":
            failed_departments: Dict = {}
            for deps in departments:
                try:
                    await notice_service.run_full_crawling_pipeline_async(
                        interval=kwargs.get('interval'),
                        delay=kwargs.get('delay'),
                        with_embeddings=True,
                        department=deps,
                        reset=reset
                    )
                except Exception as e:
                    failed_departments[department] = e
                    logging.exception(f"[{deps}] 일시적인 오류가 발생했습니다. ({e})")
                    continue

            logging.info(f"크롤링 실패 학과: {failed_departments}")

        elif _type == "me":
            for url_key in ME_URLs:
                try:
                    await notice_service.run_full_crawling_pipeline_async(
                        interval=kwargs.get('interval'),
                        delay=kwargs.get('delay'),
                        url_key=url_key,
                        with_embeddings=True,
                        reset=reset
                    )
                except Exception as e:
                    logging.exception(f"[{url_key}] 일시적인 오류가 발생했습니다. ({e})")
                    continue

    except Exception as e:
        logging.exception(f"Error while scraping({e})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--interval", dest="interval", action="store", default="10"
    )
    parser.add_argument(
        "-d", "--delay", dest="delay", action="store", default="0"
    )
    parser.add_argument(
        "-dp", "--department", dest="department", action="store", default="ALL"
    )

    parser.add_argument(
        "-r", '--reset', dest="reset", action=argparse.BooleanOptionalAction
    )

    args = parser.parse_args()

    kwargs = {
        "interval": int(args.interval),
        "delay": float(args.delay),
        "reset": bool(args.reset),
        "department": str(args.department),
    }

    asyncio.run(main(**kwargs))
