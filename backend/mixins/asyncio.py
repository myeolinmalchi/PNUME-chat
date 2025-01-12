from asyncio import Semaphore
import asyncio
from contextlib import asynccontextmanager
from functools import wraps
from typing import Optional
import logging

logger = logging.getLogger(__name__)

_Semaphore: Optional[Semaphore] = None


@asynccontextmanager
async def semaphore(limit: int = 4):
    global _Semaphore

    if _Semaphore is None:
        _Semaphore = Semaphore(limit)

    semaphore = _Semaphore

    try:
        async with semaphore:
            yield

    except Exception as e:
        logger.exception(f"비동기 작업 중 오류가 발생했습니다. ({e})")
        raise


def retry_async(times: int = 10, delay: float = 1.0):

    def decorator(func):

        @wraps(func)
        async def wrapped(*args, **kwargs):
            for _ in range(times):
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    await asyncio.sleep(delay)

            raise TimeoutError(f'{times}번의 재시도에 실패했습니다.')

        return wrapped

    return decorator