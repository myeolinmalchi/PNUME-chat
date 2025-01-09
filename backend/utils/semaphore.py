from asyncio import Semaphore
from contextlib import asynccontextmanager
from typing import Optional
from aiohttp.web import HTTPClientError, HTTPServerError
import logging

logger = logging.getLogger(__name__)


class _HTTPSemaphore:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("New ONNXRuntime instance has been created")
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, limit: int = 2):
        self.limit = 2
        self._semaphore = Semaphore(limit)

    @property
    def semaphore(self):
        return self._semaphore

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise Exception("생성자를 먼저 호출하세요.")
        assert cls._instance is not None
        return cls._instance


@asynccontextmanager
async def http_semaphore(semaphore: Optional[Semaphore] = None, limit: int = 2):
    if semaphore is None:
        http_semaphore = _HTTPSemaphore(limit)
        semaphore = http_semaphore.semaphore

    try:
        async with semaphore:
            yield
    except HTTPClientError as e:
        logger.exception(f"잘못된 HTTP 요청입니다. ({e})")
    except HTTPServerError as e:
        logger.exception(f"HTTP 서버에서 오류가 발생했습니다. ({e})")
    except Exception as e:
        logger.exception(f"HTTP 요청 처리 중 오류가 발생했습니다. ({e})")
