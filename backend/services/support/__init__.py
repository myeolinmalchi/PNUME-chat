from .dto import *
from .crawler import *
from .service import *
from .embedder import *


def create_support_service():
    support_repo = SupportRepository()
    support_embedder = SupportEmbedder()
    support_crawler = SupportCrawler()

    support_service = SupportService(
        support_repo=support_repo,
        support_embedder=support_embedder,
        support_crawler=support_crawler,
    )

    return support_service
