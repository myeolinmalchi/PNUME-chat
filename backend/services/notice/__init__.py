from typing import Literal
from .dto import *
from .service import *
from .embedder import *
from .crawler import *


def create_notice_service(_type: Literal["default", "me"] = "default"):
    semester_repo = SemesterRepository()
    notice_repo = NoticeRepository()
    notice_embedder = NoticeEmbedder()
    univ_repo = UniversityRepository()
    notice_crawler = NoticeCrawler()

    match _type:
        case "default":
            Service = NoticeService
        case "me":
            Service = NoticeMEService

    notice_service = NoticeService(
        notice_repo=notice_repo,
        notice_embedder=notice_embedder,
        notice_crawler=notice_crawler,
        university_repo=univ_repo,
        semester_repo=semester_repo
    )

    return notice_service
