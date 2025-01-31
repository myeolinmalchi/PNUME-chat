"""학지시 크롤링 스크립트

Usage:
    poetry run python3 scripts/crawler/notice.py
        -i, --interval: 한 번에 스크랩 할 게시글 수 (default: 10)
        -d, --delay: Interval간의 딜레이 (초 단위, default: 0)
        -dp, --department: 학과 (default: ALL)
        -r, --reset: 테이블 초기화 여부 (default: false)
        -rw, --rows: 목록 페이지에서 한 번에 불러올 게시글 수 (기계공학부 제외, default: 500)
"""

import argparse
import asyncio

from db.repositories import transaction
import logging

from services.support import create_support_service

import logging

import warnings

warnings.filterwarnings("ignore")


@transaction()
async def main(**kwargs):

    try:
        support_service = create_support_service()
        reset = kwargs.get("reset", False)

        await support_service.run_full_crawling_pipeline_async(
            interval=kwargs.get('interval'), delay=kwargs.get('delay'), with_embeddings=True, reset=reset
        )

    except Exception as e:
        logging.exception(f"Error while scraping({e})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interval", dest="interval", action="store", default="10")
    parser.add_argument("-d", "--delay", dest="delay", action="store", default="0")
    parser.add_argument("-dp", "--department", dest="department", action="store", default="ALL")
    parser.add_argument("-r", '--reset', dest="reset", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    kwargs = {
        "interval": int(args.interval),
        "delay": float(args.delay),
        "reset": bool(args.reset),
        "department": str(args.department),
    }

    asyncio.run(main(**kwargs))
