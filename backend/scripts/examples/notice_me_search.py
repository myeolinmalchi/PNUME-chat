"""공지사항(기계공학부) 검색 스크립트

Usage:
    $ poetry run python3 scripts/examples/notice_me_search.py --lexical-ratio <lexical-ratio> --query <query> 
        -l, --lexical-ratio: 검색시 lexical socre의 가중치 (0과 1 사이의 실수, default: 0.5)
        -q, --query: 검색 쿼리 (default: None)
"""

import asyncio
from db.repositories import NoticeMERepository
from utils.embed import embed_onnx
import argparse
import logging

logger = logging.getLogger(__name__)


async def run(lexical_ratio: float, query: str):
    notice_repo = NoticeMERepository()

    try:
        res = embed_onnx(query, chunking=False, truncate=True)

        results = notice_repo.search_notices_hybrid(
            dense_vector=res["dense"],
            sparse_vector=res["sparse"],
            lexical_ratio=lexical_ratio,
        )

        for idx, (notice, score) in enumerate(results):
            print(f"{idx + 1}. {notice.title} (score: {score:.4f})")

    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--lexical-ratio", dest="lexical_ratio", default=0.5)
    parser.add_argument("-q", "--query", dest="query", required=True)
    args = parser.parse_args()

    lexical_ratio = float(args.lexical_ratio)
    query = str(args.query)

    asyncio.run(run(lexical_ratio, query))
