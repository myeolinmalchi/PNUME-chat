from abc import abstractmethod
from typing import Generic, List, TypeVar

from aiohttp import ClientSession

D = TypeVar("D")


class BaseEmbedder(Generic[D]):

    @abstractmethod
    async def embed_async(self, item: D, sess: ClientSession) -> D:
        raise NotImplementedError("method 'aembed' must be implemented before use.")

    @abstractmethod
    async def embed_batch_async(self, items: List[D], timeout: int = 60) -> List[D]:
        raise NotImplementedError("method 'aembed_batch' must be implemented before use.")
