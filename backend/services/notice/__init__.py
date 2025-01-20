from .dto import *
from .service import *
from .embedder import *
from .crawler import *


def create_notice_service(_type: Literal["default", "me"] = "default"):
    notice_repo = NoticeRepository()
    notice_embedder = NoticeEmbedder()
    univ_repo = UniversityRepository()
    notice_crawler = create_notice_crawler(_type)

    match _type:
        case "default":
            Service = NoticeService
        case "me":
            Service = NoticeMEService

    notice_service = Service(
        notice_repo=notice_repo,
        notice_embedder=notice_embedder,
        notice_crawler=notice_crawler,
        university_repo=univ_repo
    )

    return notice_service
