from asyncio import Semaphore
import asyncio
from contextlib import asynccontextmanager
from functools import wraps
from typing import Callable, Optional
import time
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


def retry_async(times: int = 10, delay: float = 1.0, is_success=lambda _: True):

    def decorator(func):

        @wraps(func)
        async def wrapped(*args, **kwargs):
            for _ in range(times):
                try:
                    result = await func(*args, **kwargs)
                    if not is_success(result):
                        continue

                    return result
                except Exception:
                    await asyncio.sleep(delay)

            raise TimeoutError(f'{times}번의 재시도에 실패했습니다.')

        return wrapped

    return decorator


def retry_sync(
    times: int = 10, delay: float = 1.0, is_success: Callable = lambda _: True
):

    def decorator(func):

        @wraps(func)
        def wrapped(*args, **kwargs):
            for _ in range(times):
                try:
                    result = func(*args, **kwargs)
                    if not is_success(result):
                        continue

                    return result

                except Exception:
                    time.sleep(delay)

            raise TimeoutError(f'{times}번의 재시도에 실패했습니다.')

        return wrapped

    return decorator
